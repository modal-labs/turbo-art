<script lang="ts">
  import carImage from "$lib/assets/car.png";
  import valleyImage from "$lib/assets/valley.png";
  import puppyImage from "$lib/assets/puppy.png";
  import pastaImage from "$lib/assets/pasta.png";
  import abstractImage from "$lib/assets/abstract.png";

  export let promptOptionsByImage: Record<string, string[]>;
  export let imgInput: HTMLImageElement;

  export let setImage: (src: string) => void;
  export let setPrompt: (value: string) => void;
  export let setCurrentImage: (name: string) => void;
</script>

<button
  on:click={() => setCurrentImage("valley")}
  on:click={() => setImage(valleyImage)}
  on:click={() => setPrompt(promptOptionsByImage["valley"][0])}
>
  <img
    class="w-14 h-14 bg-gray"
    class:preview-active={imgInput?.src.includes(valleyImage)}
    src={valleyImage}
    alt="preview img"
  />
</button>
<button
  on:click={() => setCurrentImage("puppy")}
  on:click={() => setImage(puppyImage)}
  on:click={() => setPrompt(promptOptionsByImage["puppy"][0])}
>
  <img
    class="w-14 h-14 bg-gray"
    class:preview-active={imgInput?.src.includes(puppyImage)}
    src={puppyImage}
    alt="preview img puppy"
  />
</button>
<button
  on:click={() => setCurrentImage("car")}
  on:click={() => setImage(carImage)}
  on:click={() => setPrompt(promptOptionsByImage["car"][0])}
>
  <img
    class="w-14 h-14 bg-gray"
    class:preview-active={imgInput?.src.includes(carImage)}
    src={carImage}
    alt="preview img car"
  />
</button>
<button
  on:click={() => setCurrentImage("abstract")}
  on:click={() => setImage(abstractImage)}
  on:click={() => setPrompt(promptOptionsByImage["abstract"][0])}
>
  <img
    class="w-14 h-14 bg-gray"
    class:preview-active={imgInput?.src.includes(abstractImage)}
    src={abstractImage}
    alt="preview img"
  />
</button>
<button
  on:click={() => setCurrentImage("pasta")}
  on:click={() => setImage(pastaImage)}
  on:click={() => setPrompt(promptOptionsByImage["pasta"][0])}
>
  <img
    class="w-14 h-14 bg-gray"
    class:preview-active={imgInput?.src.includes(pastaImage)}
    src={pastaImage}
    alt="preview img"
  />
</button>

<style lang="postcss">
  .preview-active {
    @apply border-[1px] border-light-green;
  }
</style>
