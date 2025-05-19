<script lang="ts">
  import { Github, Loader, Upload, ArrowUpRight } from "lucide-svelte";
  import { onMount } from "svelte";
  import paper from "paper";
  import { throttle, debounce } from "throttle-debounce";

  import modalLogoWithText from "$lib/assets/logotype.svg";
  import Paint from "$lib/Paint.svelte";
  import easterEggImage from "$lib/assets/mocha_outside.png";
  import valleyImg from "$lib/assets/valley.png";
  import turboArtTitleGif from "$lib/assets/turbo-art-title.gif";
  import PreviewImages from "$lib/PreviewImages.svelte";
  import ImageOutput from "$lib/ImageOutput.svelte";
  import Tools from "$lib/Tools.svelte";

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
  let value: string = "";
  $: currentImageName = "valley";
  $: promptOptions = promptOptionsByImage[currentImageName];

  let imgInput: HTMLImageElement;
  let imgOutput: HTMLImageElement;
  let canvasDrawLayer: HTMLCanvasElement;
  let inputElement: HTMLInputElement;
  let fileInput: HTMLInputElement;

  let isImageUploaded = false;
  let isFirstImageGenerated = false;
  let isMobile = false;
  $: numIterations = 0;

  // we track lastUpdatedAt so that expired requests don't overwrite the latest
  let lastUpdatedAt = 0;

  // used for undo/redo functionality
  let outputImageHistory: string[] = [];
  $: currentOutputImageIndex = -1;

  $: isLoading = false;
  let isInputImageLoading = false;

  let brushSize = "sm";
  let paint = "#000000";
  const radiusByBrushSize: Record<string, number> = {
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
  };

  function setPaint(e: CustomEvent<string>) {
    paint = e.detail;
  }
  function setBrushSize(e: CustomEvent<string>) {
    brushSize = e.detail;
  }

  function checkBreakpoint() {
    isMobile = window.innerWidth < 640;
  }

  onMount(() => {
    // Manual mobile check is needed because of binding issues with <ImageOutput />
    checkBreakpoint();
    window.addEventListener("resize", checkBreakpoint);

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
    return () => window.removeEventListener("resize", checkBreakpoint);
  });

  function onLoadInputImg(event: Event) {
    resizeImage(event);

    isImageUploaded = true;
    isInputImageLoading = false;

    // kick off an inference on first image load so output image is populated as well
    // otherwise it will be empty
    if (!isFirstImageGenerated) {
      generateOutputImage();
      isFirstImageGenerated = true;
    }
  }

  function setImage(src: string) {
    isInputImageLoading = true;
    imgInput.src = src;

    outputImageHistory.unshift(src);
    currentOutputImageIndex = 0;

    function loopGenerate() {
      if (isInputImageLoading) {
        // wait for onload before generating an image
        setTimeout(loopGenerate, 100);
        return;
      }

      generateOutputImage();
    }

    loopGenerate();
  }

  function setPrompt(prompt: string) {
    value = prompt;
    generateOutputImage();
  }

  // Our images need to be sized 320x320 for both input and output
  // This is important because we combine the canvas layer with the image layer
  // so the pixels need to matchup.
  function resizeImage(event: Event) {
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
  }

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
    () => generateOutputImage(),
    { noLeading: false, noTrailing: false }
  );

  const debouncedgenerateOutputImage = debounce(
    100,
    () => generateOutputImage(),
    { atBegin: false }
  );

  function movetoCanvas() {
    imgInput.src = imgOutput.src;
  }

  function downloadImage() {
    let a = document.createElement("a");
    a.href = imgOutput.src;
    a.download = "modal-generated-image.jpeg";
    a.click();
  }

  function enhance() {
    generateOutputImage(true, 10);
  }

  function redoOutputImage() {
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
  }

  function undoOutputImage() {
    if (currentOutputImageIndex < outputImageHistory.length - 1) {
      currentOutputImageIndex += 1;
      imgOutput.src = outputImageHistory[currentOutputImageIndex];
    }
  }

  function resetInput() {
    if (fileInput) {
      fileInput.value = "";
    }
  }

  async function generateOutputImage(
    useOutputImage: boolean = false,
    iterations: number = 2
  ) {
    isLoading = true;
    const data = await getImageData(useOutputImage);

    const formData = new FormData();
    formData.append("image", data, "image.jpg");
    formData.append("prompt", value);
    formData.append("num_iterations", iterations.toString());

    const sentAt = new Date().getTime();
    try {
      const res = await fetch((window as any).INFERENCE_BASE_URL, {
        method: "POST",
        body: formData,
      });
      const blob = await res.blob();

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

      isFirstImageGenerated = true;
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="flex flex-col items-center md:pt-12 text-light-green">
  <div class="md:max-w-screen-lg lg:w-[1024px] w-full">
    <div
      class="bg-light-green/10 sm:border sm:border-light-green/20 md:rounded-lg px-4 py-6 sm:p-6 flex flex-col gap-6"
    >
      <div class="flex flex-col gap-3 sm:gap-1">
        <div class="flex items-center justify-between">
          <img width={175} src={turboArtTitleGif} alt="Turbo.Art" />
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://github.com/modal-labs/turbo-art/tree/main"
            class="btns-container justify-center font-medium"
          >
            <Github size={20} />View Code
          </a>
        </div>
        <div class="text-sm">
          The image generation is powered by Stability's <a
            target="_blank"
            rel="noopener noreferrer"
            class="underline"
            href="https://stability.ai/news/stability-ai-sdxl-turbo"
            >SDXL Turbo</a
          >
        </div>
      </div>

      <div class="flex flex-col gap-4">
        <h3 class="heading">Prompt</h3>
        <div class="flex flex-col sm:flex-row gap-2 lg:flex-nowrap flex-wrap">
          {#each promptOptions as item}
            <button
              class="italic flex-shrink-0 text-xs px-4 py-2 border border-light-green/30 rounded-full text-light-green/60"
              class:prompt-active={item === value}
              on:click={() => setPrompt(item)}>{item}</button
            >
          {/each}
        </div>
        <input
          class="rounded-full bg-light-green/10 py-4 px-6 w-full text-sm"
          bind:value
          bind:this={inputElement}
          on:input={debouncedgenerateOutputImage}
          placeholder="Enter prompt here"
        />
      </div>

      <div class="flex flex-col md:flex-row gap-6 md:gap-0">
        <div
          class="flex flex-col gap-6 md:pr-4 md:border-r md:border-light-green/10 w-full"
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
              ></canvas>
            </div>
            {#if isMobile}
              <ImageOutput
                bind:imgOutput
                {isFirstImageGenerated}
                {resizeImage}
              />
            {/if}
            <div class="flex gap-4">
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
              <div class="sm:hidden block">
                <Tools
                  {undoOutputImage}
                  {redoOutputImage}
                  {enhance}
                  {movetoCanvas}
                  {downloadImage}
                />
              </div>
            </div>
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
          <label
            for="file-upload"
            class="btns-container flex-col w-fit cursor-pointer w-full sm:w-fit"
          >
            <div class="flex items-center gap-2 font-medium">
              <Upload size={16} />
              Upload Image (JPG, PNG)
            </div>
          </label>
        </div>

        <div class="flex flex-col gap-6 w-full md:pl-6">
          <div class="flex flex-col gap-1 sm:block hidden">
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

          <div class="flex gap-4 flex-col sm:flex-row md:flex-col lg:flex-row">
            {#if !isMobile}
              <ImageOutput
                bind:imgOutput
                {isFirstImageGenerated}
                {resizeImage}
              />
            {/if}
            <div class="sm:block hidden">
              <Tools
                {undoOutputImage}
                {redoOutputImage}
                {enhance}
                {movetoCanvas}
                {downloadImage}
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      class="lg:w-full flex mt-6 mb-8 md:mb-12 mx-2 md:mx-6 lg:mx-0 justify-between items-center"
    >
      <div class="flex items-center gap-3 font-degular">
        Built with <img
          class="modal-logo"
          alt="Modal logo"
          src={modalLogoWithText}
        />
      </div>
      <a
        target="_blank"
        rel="noopener noreferrer"
        href="https://modal.com"
        class="button px-5 py-[6px] font-medium"
      >
        Get Started <ArrowUpRight size={16} />
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

  .prompt-active {
    @apply text-light-green border-light-green/80;
  }
</style>
