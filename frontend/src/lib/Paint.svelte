<script lang="ts">
  import { Eraser } from "lucide-svelte";
  import { Color } from "color-picker-svelte";

  import smallPaintIcon from "$lib/assets/sm-paint-icon.svg";
  import extraSmallPaintIcon from "$lib/assets/xs-paint-icon.svg";
  import mediumPaintIcon from "$lib/assets/md-paint-icon.svg";
  import circlePaintIcon from "$lib/assets/circle-paint-icon.svg";
  import squarePaintIcon from "$lib/assets/square-paint-icon.svg";
  import polygonPaintIcon from "$lib/assets/polygon-paint-icon.svg";
  import largePaintIcon from "$lib/assets/lg-paint-icon.svg";
  import { createEventDispatcher } from "svelte";
  import type { ShapeType } from "../App.svelte";

  const dispatch = createEventDispatcher();

  export let paint: string;
  export let brushSize: string;
  export let brushShape: ShapeType;
  $: color = new Color(paint);
  $: {
    handleSetPaint(color.toHexString());
  }

  const handleClearCanvas = () => {
    dispatch("clearCanvas");
  };

  const handleSetPaint = (paint: string) => {
    dispatch("setPaint", paint);
  };

  const handleSetBrushSize = (size: string) => {
    dispatch("setBrushSize", size);
    dispatch("setBrushShape", "brush");
  };

  const handleSetBrushShape = (shape: ShapeType) => {
    dispatch("setBrushShape", shape);
  };
</script>

<div class="flex flex-col gap-3">
  <button
    class="flex items-center gap-2.5 w-full text-xs cursor-pointer hover:text-light-green clear-button hover:bg-light-green/20 active:bg-light-green/30 bg-light-green/10 focus-visible:outline-light-green focus-visible:outline outline-offset-1"
    on:click={() => handleClearCanvas()}
  >
    <Eraser size={16} /> Clear
  </button>

  <div class="tools-container flex-col items-center">
    <div class="colors">
      <button
        on:click={() => handleSetPaint("#000000")}
        class="circle bg-black focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#000000"}
      />
      <button
        on:click={() => handleSetPaint("#ffffff")}
        class="circle bg-white focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#ffffff"}
      />
      <button
        on:click={() => handleSetPaint("#2613fd")}
        class="circle bg-[#2613FD] focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#2613fd"}
      />
      <button
        on:click={() => handleSetPaint("#5e57b3")}
        class="circle bg-[#5E57B3] focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#5e57b3"}
      />
      <button
        on:click={() => handleSetPaint("#fd139f")}
        class="circle bg-[#FD139F] focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#fd139f"}
      />
      <button
        on:click={() => handleSetPaint("#a4fd13")}
        class="circle bg-[#A4FD13] focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#a4fd13"}
      />
      <button
        on:click={() => handleSetPaint("#fd1321")}
        class="circle bg-[#FD1321] focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#fd1321"}
      />
      <button
        on:click={() => handleSetPaint("#ff9900")}
        class="circle bg-[#F90] focus-visible:outline-light-green focus-visible:outline outline-offset-1"
        class:circle-active={paint === "#ff9900"}
      />
    </div>

    <div
      class="row flex border-light-green/10 border-t pt-2.5 justify-between w-full"
    >
      <button
        on:click={() => handleSetBrushSize("xs")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "brush" && brushSize === "xs"}
          src={extraSmallPaintIcon}
          alt="extrasmall paint icon"
        />
      </button>
      <button
        on:click={() => handleSetBrushSize("sm")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "brush" && brushSize === "sm"}
          src={smallPaintIcon}
          alt="small paint icon"
        />
      </button>
    </div>
    <div class="row flex justify-between w-full">
      <button
        on:click={() => handleSetBrushSize("md")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "brush" && brushSize === "md"}
          src={mediumPaintIcon}
          alt="medium paint icon"
        />
      </button>
      <button
        on:click={() => handleSetBrushSize("lg")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "brush" && brushSize === "lg"}
          src={largePaintIcon}
          alt="large paint icon"
        />
      </button>
    </div>

    <div
      class="shape-container flex justify-between w-full border-light-green/10 border-t pt-2.5"
    >
      <button
        on:click={() => handleSetBrushShape("circle")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "circle"}
          src={circlePaintIcon}
          alt="circle paint icon"
        />
      </button>
      <button
        on:click={() => handleSetBrushShape("square")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "square"}
          src={squarePaintIcon}
          alt="square paint icon"
        />
      </button>
    </div>
    <div class="shape-container flex justify-between w-full">
      <button
        on:click={() => handleSetBrushShape("polygon")}
        class="focus-visible:outline-light-green focus-visible:outline outline-offset-1 tool-button"
      >
        <img
          class="brush"
          class:brush-active={brushShape === "polygon"}
          src={polygonPaintIcon}
          alt="polygon paint icon"
        />
      </button>
    </div>
  </div>
</div>

<style lang="postcss">
  .circle {
    @apply w-5 h-5 rounded-full;
  }

  .circle-active {
    @apply outline outline-light-green outline-offset-1;
  }

  .brush {
    filter: brightness(0) saturate(100%) invert(64%) sepia(27%) saturate(194%)
      hue-rotate(69deg) brightness(89%) contrast(89%);
  }

  .brush-active {
    filter: invert(100%) sepia(6%) saturate(7487%) hue-rotate(293deg)
      brightness(103%) contrast(118%);
  }

  .clear-button {
    @apply flex py-2 px-3 border rounded-[10px] border-light-green/5  w-fit cursor-auto;
  }

  .tool-button {
    @apply w-6 h-6 flex items-center justify-center shrink-0;
  }

  .row {
    @apply flex gap-2;
  }

  .colors {
    @apply grid grid-cols-2 gap-3 py-2;
  }
</style>
