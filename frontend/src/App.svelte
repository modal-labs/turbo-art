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
    Sparkle,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import paper from "paper";
  import { throttle, debounce } from "throttle-debounce";

  import BackgroundGradient from "$lib/BackgroundGradient.svelte";
  import modalLogoWithText from "$lib/assets/logotype.svg";
  import Paint from "$lib/Paint.svelte";
  import easterEggImage from "$lib/assets/mocha_outside.png";
  import valleyImg from "$lib/assets/valley.png";
  import turboArtTitleGif from "$lib/assets/turbo-art-title.gif";
  import resolveConfig from "tailwindcss/resolveConfig";
  import tailwindConfig from "../tailwind.config.js";
  import PreviewImages from "$lib/PreviewImages.svelte";

  const fullConfig = resolveConfig(tailwindConfig);
  const breakpointSm = parseInt(fullConfig.theme.screens.sm);
  $: isMobile = false;

  const handleWindowResize = () => {
    const isSmallWindow = window.innerWidth <= breakpointSm;
    isMobile = isSmallWindow;
  };

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
  let value: string = promptOptionsByImage["valley"][0];
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
    handleWindowResize();

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
    { noLoading: false, noTrailing: false },
  );

  const debouncedgenerateOutputImage = debounce(
    100,
    () => {
      generateOutputImage();
    },
    { atBegin: false },
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
    iterations: number = 2,
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

<svelte:window on:resize={handleWindowResize} />
<BackgroundGradient />
<main class="flex flex-col items-center sm:pt-12">
  <div class="container">
    <div class="flex items-center justify-between">
      <div>
        <img
          width={200}
          class="absolute mt-[-55px] z-[-1] left-0 sm:left-auto scale-75 sm:scale-100"
          src={turboArtTitleGif}
          alt="Turbo.Art"
        />
        <div class="h-28" />
      </div>
      <a
        href="https://github.com/modal-labs/turbo-art/tree/main"
        class="btns-container justify-center py-2 px-5 font-medium"
      >
        <Github size={16} />View Code
      </a>
    </div>
    <div class="font-sm">
      The image generation is powered by Stability's <a
        class="primary underline"
        href="https://stability.ai/news/stability-ai-sdxl-turbo">SDXL Turbo</a
      >
    </div>

    <div class="mt-3">
      {#if !isMobile}
        <h3 class="mb-3 font-semibold">Prompt</h3>
        <div class="flex flex-col sm:flex-row gap-2">
          {#each promptOptions as item}
            <button
              class="btns-container text-xs py-0.5 px-2"
              style="width:fit-content"
              on:click={() => setPrompt(item)}>{item}</button
            >
          {/each}
        </div>
        <input
          class="rounded-lg border border-white/20 bg-white/10 py-4 px-6 outline-none w-full mt-3"
          bind:value
          bind:this={inputElement}
          on:input={debouncedgenerateOutputImage}
        />
      {/if}

      {#if isMobile}
        <div class="mt-3">
          <PreviewImages
            {promptOptionsByImage}
            {imgInput}
            {setImage}
            setCurrentImage={(name) => (currentImageName = name)}
            setPrompt={(v) => (value = v)}
          />
        </div>
      {/if}
    </div>

    <div class="mt-3 flex flex-col sm:flex-row">
      <div class="pr-7 sm:border-r border-white/10 flex flex-col sm:flex-row">
        <div>
          <div class="pb-3">
            <div class="mb-2 font-medium flex gap-1 items-center">
              Canvas
              {#if isMobile}
                {#if isLoading}
                  <Loader size={14} class="animate-spin" />
                {/if}
              {/if}
            </div>
            <div>Draw on the image to generate a new one</div>
          </div>

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
            class="w-[320px] h-[320px] z-1"
          />

          {#if !isMobile}
            <div class="mt-3 flex gap-4">
              <PreviewImages
                {promptOptionsByImage}
                {imgInput}
                {setImage}
                setCurrentImage={(name) => (currentImageName = name)}
                setPrompt={(v) => (value = v)}
              />
            </div>
          {/if}
        </div>

        {#if !isMobile}
          <div class="sm:ml-3 mt-3 sm:mt-[68px]">
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
        {/if}
      </div>

      <div class="sm:pl-7 flex flex-col sm:flex-row">
        <div>
          {#if !isMobile}
            <div class="pb-3">
              <div class="mb-2 flex items-center gap-1 font-medium">
                Output
                {#if isLoading}
                  <Loader size={14} class="animate-spin" />
                {/if}
              </div>
              <div>Generated Image (iterations: {numIterations})</div>
            </div>
          {/if}

          <img
            alt="loading..."
            bind:this={imgOutput}
            class="w-[320px] h-[320px] bg-[#D9D9D9]"
            class:hidden={!firstImageGenerated}
            on:load={resizeImage}
          />
        </div>

        {#if isMobile}
          <div class="mt-3">
            <h3 class="mb-3 font-semibold">Prompt</h3>
            <div class="flex flex-col sm:flex-row gap-2">
              {#each promptOptions as item}
                <button
                  class="btns-container text-xs py-0.5 px-2"
                  style="width:fit-content"
                  on:click={() => setPrompt(item)}>{item}</button
                >
              {/each}
            </div>
            <input
              class="rounded-lg border border-white/20 bg-white/10 py-4 px-6 outline-none w-full mt-3"
              bind:value
              bind:this={inputElement}
              on:input={debouncedgenerateOutputImage}
            />
          </div>
        {/if}
        <div class="flex sm:justify-between sm:ml-6">
          {#if isMobile}
            <div class="mt-3 mr-3">
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
          {/if}
          <div class="flex flex-col gap-4 mt-3 sm:mt-[68px]">
            <div class="btns-container justify-space-between">
              <button class="text-xs flex gap-1.5" on:click={undoOutputImage}>
                <Undo size={16} />Back
              </button>
              <div class="w-[1px] h-4 bg-white/10" />
              <button class="text-xs flex gap-1.5" on:click={redoOutputImage}>
                <Redo size={16} />Next
              </button>
            </div>
            <button
              class="special-button text-xs btns-container"
              on:click={enhance}
            >
              <Sparkle size={16} />Enhance
            </button>
            <button class="text-xs btns-container" on:click={movetoCanvas}>
              <ArrowLeftSquare size={16} />Move to Canvas
            </button>

            <button class="text-xs btns-container" on:click={downloadImage}>
              <ArrowDownToLine size={16} /> Download
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="mt-3">
      <input
        type="file"
        accept="image/*"
        id="file-upload"
        hidden
        bind:this={fileInput}
        on:change={loadImage}
        on:click={resetInput}
      />
      <label
        for="file-upload"
        class="button flex-col w-[446px] h-[76px] max-w-full"
      >
        <div class="flex items-center gap-2 font-medium">
          <Upload size={16} />
          Upload Image
        </div>
        <span class="text-xs">PNG, JPEG</span>
      </label>
    </div>
  </div>

  <div
    class="w-full container flex mt-4 mb-[92px] justify-between items-center"
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
</main>

<style lang="postcss">
  .container {
    @apply bg-white/10 border border-white/20 rounded-lg p-6 max-w-screen-lg;
  }

  .btns-container {
    @apply flex items-center gap-2.5 py-2 px-3 border rounded-[10px] border-white/5 bg-white/10;
    width: 144px;
  }

  .button {
    @apply border border-primary bg-primary/20 rounded-lg justify-center items-center flex gap-2 cursor-pointer;
  }

  .modal-logo {
    width: 108px;
    height: 32px;
  }

  .preview-active {
    @apply border-2 border-primary;
  }

  .special-button {
    background: linear-gradient(
        93deg,
        rgba(255, 83, 83, 0.6) -16.83%,
        rgba(255, 35, 141, 0.6) 11.43%,
        rgba(91, 127, 255, 0.6) 61.11%,
        rgba(0, 255, 87, 0.6) 108.92%
      ),
      rgba(255, 255, 255, 0.1);
    border: none;
  }
</style>
