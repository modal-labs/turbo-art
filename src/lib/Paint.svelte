<script lang="ts">
  import { Eraser } from "lucide-svelte";
  import { Color } from "color-picker-svelte";

  import smallPaintIcon from "$lib/assets/sm-paint-icon.svg";
  import extraSmallPaintIcon from "$lib/assets/xs-paint-icon.svg";
  import mediumPaintIcon from "$lib/assets/md-paint-icon.svg";
  import largePaintIcon from "$lib/assets/lg-paint-icon.svg";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher<{
    clearCanvas: void;
    setPaint: string;
    setBrushSize: string;
  }>();

  export let paint: string;
  export let brushSize: string;
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
  };

  const palette = [
    { hex: "#000000", name: "black" },
    { hex: "#ffffff", name: "white" },
    { hex: "#2613fd", name: "blue" },
    { hex: "#5e57b3", name: "indigo" },
    { hex: "#fd139f", name: "pink" },
    { hex: "#a4fd13", name: "lime" },
    { hex: "#fd1321", name: "red" },
    { hex: "#ff9900", name: "orange" },
  ];
</script>

<div class="flex flex-col gap-3">
  <button
    class="tool gap-2.5 w-full text-xs"
    on:click={() => handleClearCanvas()}
  >
    <Eraser size={16} /> Clear
  </button>

  <div class="tool flex-col">
    <div class="grid grid-cols-2 gap-2">
      {#each palette as { hex, name }}
        <button
          aria-label="{name} paint"
          on:click={() => handleSetPaint(hex)}
          class="circle"
          class:circle-active={paint === hex}
          style:background={hex}
        ></button>
      {/each}
    </div>

    <hr class="border-light-green/10" />

    <div class="grid grid-cols-2 gap-1 w-full">
      <button class="brush-btn" on:click={() => handleSetBrushSize("xs")}>
        <img
          class="brush"
          class:brush-active={brushSize === "xs"}
          src={extraSmallPaintIcon}
          alt="extrasmall paint icon"
        />
      </button>
      <button class="brush-btn" on:click={() => handleSetBrushSize("sm")}>
        <img
          class="brush"
          class:brush-active={brushSize === "sm"}
          src={smallPaintIcon}
          alt="small paint icon"
        />
      </button>
      <button class="brush-btn" on:click={() => handleSetBrushSize("md")}>
        <img
          class="brush"
          class:brush-active={brushSize === "md"}
          src={mediumPaintIcon}
          alt="medium paint icon"
        />
      </button>
      <button class="brush-btn" on:click={() => handleSetBrushSize("lg")}>
        <img
          class="brush"
          class:brush-active={brushSize === "lg"}
          src={largePaintIcon}
          alt="large paint icon"
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
    @apply border-[1px] border-light-green;
  }

  .brush-btn {
    @apply w-6 h-5 flex items-center justify-center;
  }

  .brush {
    filter: invert(100%) sepia(6%) saturate(7487%) hue-rotate(293deg)
      brightness(103%) contrast(118%);
  }

  .brush-active {
    filter: brightness(0) saturate(100%) invert(64%) sepia(27%) saturate(194%)
      hue-rotate(69deg) brightness(89%) contrast(89%);
  }

  .tool {
    @apply flex gap-2.5 py-2 px-3 border rounded-[10px] border-light-green/5 bg-light-green/10 w-fit;
  }
</style>
