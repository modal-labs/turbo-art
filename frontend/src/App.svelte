<script lang="ts">
  import {
    Github,
    Loader,
    Upload,
    Undo,
    Redo,
    ArrowDownToLine,
    ArrowLeftSquare,
    MoveUpRight,
    Wand,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import paper from "paper";
  import { throttle, debounce } from "throttle-debounce";

  import modalLogoWithText from "$lib/assets/logotype.svg";
  import Paint from "$lib/Paint.svelte";
  import easterEggImage from "$lib/assets/mocha_outside.png";
  import valleyImg from "$lib/assets/valley.png";
  import turboArtTitleGif from "$lib/assets/turbo-art-title.gif";
  import PreviewImages from "$lib/PreviewImages.svelte";

  const promptOptionsByImage: Record<string, string[]> = {
    abstract: [
      "cityscape, studio ghibli, illustration",
      "a scene from Jodorowsky’s Dune, surreal, sandworm in the background",
      "lunar landing in the style of a van gogh painting",
    ],
    puppy: [
      "cartoon bear, pixar, bright, happy",
      "evil cybernetic wolf, watercolor",
      "3d claymation Shiba Inu",
    ],
    car: [
      "neon lights, comic book",
      "Tesla driving on the Moon, planets in the background",
      "futuristic car in cyberpunk cityscape, photorealistic",
    ],
    valley: [
      "cityscape, studio ghibli, illustration",
      "Mediterranean city, impressionist painting, purple tint",
      "coral reef in the style of Spongebob, cartoon, animated",
    ],
    pasta: [
      "coral reef in the style of Spongebob, cartoon, animated",
      "sci-fi scene from star wars, spaceships in the background, cinematic",
      "italian food, cezanne painting",
    ],
  };
  let value: string = "Enter prompt here";
  $: currentImageName = "valley";
  $: promptOptions = promptOptionsByImage[currentImageName];

  let imgInput: HTMLImageElement;
  let imgOutput: HTMLImageElement;
  let canvasDrawLayer: HTMLCanvasElement;
  let inputElement: HTMLInputElement;
  let fileInput: HTMLInputElement;

  let isImageUploaded = false;
  let firstImageGenerated = false;
  $: numIterations = 0;

  // we track lastUpdatedAt so that expired requests don't overwrite the latest
  let lastUpdatedAt = 0;

  // used for undo/redo functionality
  let outputImageHistory: string[] = [];
  $: currentOutputImageIndex = -1;

  $: isLoading = false;
  let isInputImageLoading = false;

  $: brushSize = "sm";
  $: paint = "black"; // can be hex
  const radiusByBrushSize: Record<string, number> = {
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
  };
  const setPaint = (e: CustomEvent<string>) => {
    paint = e.detail;
  };
  const setBrushSize = (e: CustomEvent<string>) => {
    brushSize = e.detail;
  };

  onMount(() => {
    /* 
      Setup paper.js for canvas which is a layer above our input image.
      Paper is used for drawing/paint functionality.
    */
    paper.setup(canvasDrawLayer);
    const tool = new paper.Tool();

    let path: paper.Path;

    tool.onMouseDown = (event: paper.ToolEvent) => {
      path = new paper.Path();
      path.strokeColor = new paper.Color(paint);
      path.strokeWidth = radiusByBrushSize[brushSize] * 4;
      path.add(event.point);

      throttledgenerateOutputImage();
    };

    tool.onMouseDrag = (event: paper.ToolEvent) => {
      path.add(event.point);

      throttledgenerateOutputImage();
    };

    if (inputElement) {
      inputElement.focus();
    }

    setImage(valleyImg);
  });

  const onLoadInputImg = (event: Event) => {
    resizeImage(event);

    isImageUploaded = true;
    isInputImageLoading = false;

    // kick off an inference on first image load so output image is populated as well
    // otherwise it will be empty
    if (!firstImageGenerated) {
      generateOutputImage();
      firstImageGenerated = true;
    }
  };

  const setImage = (src: string) => {
    isInputImageLoading = true;
    imgInput.src = src;

    outputImageHistory.unshift(src);
    currentOutputImageIndex = 0;

    const loopGenerate = () => {
      if (isInputImageLoading) {
        // wait for onload before generating an image
        setTimeout(loopGenerate, 100);
        return;
      }

      generateOutputImage();
    };

    loopGenerate();
  };

  const setPrompt = (prompt: string) => {
    value = prompt;
    generateOutputImage();
  };

  // Our images need to be sized 320x320 for both input and output
  // This is important because we combine the canvas layer with the image layer
  // so the pixels need to matchup.
  const resizeImage = (event: Event) => {
    const target = event.target as HTMLImageElement;

    let newWidth;
    let newHeight;
    if (target.naturalWidth > target.naturalHeight) {
      const aspectRatio = target.naturalHeight / target.naturalWidth;
      newWidth = 320;
      newHeight = newWidth * aspectRatio;
    } else {
      const aspectRatio = target.naturalWidth / target.naturalHeight;
      newHeight = 320;
      newWidth = newHeight * aspectRatio;
    }

    target.style.height = `${newHeight}px`;
    target.style.width = `${newWidth}px`;
  };

  function loadImage(e: Event) {
    const target = e.target as HTMLInputElement;
    if (!target || !target.files) return;
    const file = target.files[0];

    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e?.target?.result && typeof e.target.result === "string") {
          isImageUploaded = true;
          setImage(e?.target.result);
        }
      };

      reader.readAsDataURL(file);
    }
  }

  function getImageData(useOutputImage: boolean = false): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = 320;
      tempCanvas.height = 320;
      const tempCtx = tempCanvas.getContext("2d");
      if (!tempCtx) {
        reject("no context");
        return;
      }

      if (useOutputImage) {
        tempCtx.drawImage(imgOutput, 0, 0, 320, 320);
      } else {
        // combines the canvas with the input image so that the
        // generated image contains edits made by paint brush
        tempCtx.drawImage(imgInput, 0, 0, 320, 320);
        tempCtx.drawImage(canvasDrawLayer, 0, 0, 320, 320);
      }

      tempCanvas.toBlob((blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject("blob creation failed");
        }
      }, "image/jpeg");
    });
  }

  const throttledgenerateOutputImage = throttle(
    250,
    () => {
      generateOutputImage();
    },
    { noLoading: false, noTrailing: false }
  );

  const debouncedgenerateOutputImage = debounce(
    100,
    () => {
      generateOutputImage();
    },
    { atBegin: false }
  );

  const movetoCanvas = () => {
    imgInput.src = imgOutput.src;
  };

  const downloadImage = () => {
    let a = document.createElement("a");
    a.href = imgOutput.src;
    a.download = "modal-generated-image.jpeg";
    a.click();
  };

  const enhance = () => {
    generateOutputImage(true, 10);
  };

  const redoOutputImage = () => {
    if (currentOutputImageIndex > 0 && outputImageHistory.length > 1) {
      currentOutputImageIndex -= 1;
      imgOutput.src = outputImageHistory[currentOutputImageIndex];
    } else {
      if (value === "good boy") {
        setImage(easterEggImage);
        return;
      }
      generateOutputImage(true);
    }
  };

  const undoOutputImage = () => {
    if (currentOutputImageIndex < outputImageHistory.length - 1) {
      currentOutputImageIndex += 1;
      imgOutput.src = outputImageHistory[currentOutputImageIndex];
    }
  };

  const resetInput = () => {
    if (fileInput) {
      fileInput.value = "";
    }
  };

  const generateOutputImage = async (
    useOutputImage: boolean = false,
    iterations: number = 2
  ) => {
    isLoading = true;
    const data = await getImageData(useOutputImage);

    const formData = new FormData();
    formData.append("image", data, "image.jpg");
    formData.append("prompt", value);
    formData.append("num_iterations", iterations.toString());

    const sentAt = new Date().getTime();
    fetch(window.INFERENCE_BASE_URL, {
      method: "POST",
      body: formData,
    })
      .then((res) => res.blob())
      .then((blob) => {
        if (sentAt > lastUpdatedAt) {
          const imageURL = URL.createObjectURL(blob);
          outputImageHistory = [imageURL, ...outputImageHistory];
          if (outputImageHistory.length > 10) {
            outputImageHistory = outputImageHistory.slice(0, 10);
          }
          imgOutput.src = imageURL;
          if (useOutputImage) {
            numIterations += iterations;
          } else {
            numIterations = 1;
          }
          lastUpdatedAt = sentAt;
        }

        firstImageGenerated = true;
      })
      .finally(() => (isLoading = false));
  };
</script>

<main class="flex flex-col items-center md:pt-12 text-light-green">
  <div class="md:max-w-screen-lg md:w-[1024px] w-full">
    <div
      class="bg-light-green/10 sm:border sm:border-light-green/20 md:rounded-lg p-2 sm:p-6 flex flex-col gap-6"
    >
      <div class="flex flex-col gap-3 sm:gap-1">
        <div class="flex items-center justify-between">
          <img width={200} src={turboArtTitleGif} alt="Turbo.Art" />
          <a
            href="https://github.com/modal-labs/turbo-art/tree/main"
            class="btns-container justify-center font-medium"
          >
            <Github size={20} />View Code
          </a>
        </div>
        <div class="text-sm">
          The image generation is powered by Stability's <a
            class="primary underline"
            href="https://stability.ai/news/stability-ai-sdxl-turbo"
            >SDXL Turbo</a
          >
        </div>
      </div>

      <div class="flex flex-col gap-4">
        <h3 class="heading">Prompt</h3>
        <div class="flex flex-col sm:flex-row gap-2 md:flex-nowrap flex-wrap">
          {#each promptOptions as item}
            <button
              class="italic flex-shrink-0 text-xs px-4 py-2 border border-light-green/30 rounded-full"
              on:click={() => setPrompt(item)}>{item}</button
            >
          {/each}
        </div>
        <input
          class="rounded-full bg-light-green/10 py-4 px-6 w-full text-sm"
          bind:value
          bind:this={inputElement}
          on:input={debouncedgenerateOutputImage}
        />
      </div>

      <div class="flex flex-col md:flex-row gap-6 md:gap-0">
        <div
          class="flex flex-col gap-6 md:border-r md:border-light-green/10 w-full"
        >
          <div class="flex flex-col gap-1">
            <div class="heading flex gap-1 items-center">
              Canvas
              {#if isLoading}
                <Loader size={14} class="animate-spin" />
              {/if}
            </div>
            <div class="text-xs">Draw on the image to generate a new one</div>
          </div>

          <div class="flex gap-6 flex-col sm:flex-row">
            <div>
              <img
                alt="input"
                bind:this={imgInput}
                class="absolute bg-[#D9D9D9] pointer-events-none z-[-1]"
                class:hidden={!isImageUploaded}
                on:load={onLoadInputImg}
              />
              <canvas
                bind:this={canvasDrawLayer}
                width={320}
                height={320}
                class="z-1"
              />
            </div>
            <Paint
              {paint}
              {brushSize}
              on:clearCanvas={() => {
                paper.project.activeLayer.removeChildren();
                paper.view.update();
                generateOutputImage();
              }}
              on:setPaint={setPaint}
              on:setBrushSize={setBrushSize}
            />
          </div>
          <div class="flex gap-2">
            <PreviewImages
              {promptOptionsByImage}
              {imgInput}
              {setImage}
              setCurrentImage={(name) => (currentImageName = name)}
              setPrompt={(v) => (value = v)}
            />
          </div>
          <input
            type="file"
            accept="image/*"
            id="file-upload"
            hidden
            bind:this={fileInput}
            on:change={loadImage}
            on:click={resetInput}
          />
          <label for="file-upload" class="btns-container flex-col w-fit">
            <div class="flex items-center gap-2 font-medium">
              <Upload size={16} />
              Upload Image (PNG, JPEG)
            </div>
          </label>
        </div>

        <div class="flex flex-col gap-4 w-full md:pl-6">
          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-1 heading">
              Output
              {#if isLoading}
                <Loader size={14} class="animate-spin" />
              {/if}
            </div>
            <div class="text-xs">
              Generated Image (iterations: {numIterations})
            </div>
          </div>

          <div class="flex gap-4 flex-col sm:flex-row">
            <img
              width={320}
              height={320}
              alt="loading..."
              bind:this={imgOutput}
              class="bg-[#D9D9D9]"
              class:hidden={!firstImageGenerated}
              on:load={resizeImage}
            />
            <div class="flex flex-col sm:gap-4 gap-2">
              <div class="tools-container">
                <button class="text-xs flex gap-1" on:click={undoOutputImage}>
                  <Undo size={16} />Back
                </button>
                <div class="w-[1px] h-4 bg-white/10" />
                <button class="text-xs flex gap-1" on:click={redoOutputImage}>
                  <Redo size={16} />Next
                </button>
              </div>
              <button
                class="special-button text-xs tools-container sm bg-muted-yellow"
                on:click={enhance}
              >
                <Wand size={16} />Enhance
              </button>
              <button
                class="text-xs tools-container tools-container-sm"
                on:click={movetoCanvas}
              >
                <ArrowLeftSquare size={16} />Move to Canvas
              </button>

              <button
                class="text-xs tools-container tools-container-sm"
                on:click={downloadImage}
              >
                <ArrowDownToLine size={16} /> Download
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      class="md:w-full flex mt-6 md:mb-[92px] mb-8 mx-2 sm:mx-6 md:mx-0 justify-between items-center"
    >
      <div class="flex items-center gap-2">
        Built with <img
          class="modal-logo"
          alt="Modal logo"
          src={modalLogoWithText}
        />
      </div>
      <a href="https://modal.com" class="button px-5 py-[6px] font-medium">
        Get Started <MoveUpRight size={16} />
      </a>
    </div>
  </div>
</main>

<style lang="postcss">
  .heading {
    @apply text-2xl font-degular;
  }

  .btns-container {
    @apply flex items-center gap-2 py-2 px-6 border rounded-full border-light-green/30 text-sm;
  }

  .button {
    @apply bg-primary rounded-full justify-center items-center flex gap-2 text-black text-sm;
  }

  .modal-logo {
    width: 108px;
    height: 32px;
  }

  :global(.tools-container) {
    @apply flex gap-2.5 py-2 px-3 border rounded-[10px] border-light-green/10 bg-light-green/10 w-fit;
  }
  .tools-container,
  .tools-container-sm {
    @apply gap-1.5 px-2;
  }

  @media (min-width: 640px) {
    .tools-container-sm {
      @apply w-full;
    }
  }
</style>
