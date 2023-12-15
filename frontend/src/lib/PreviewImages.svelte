<script lang="ts">
    import carImage from "$lib/assets/car.png";
    import beachImage from "$lib/assets/beach.png";
    import puppyImage from "$lib/assets/puppy.png";
    import abstractImage from "$lib/assets/abstract.png";
    import type { AlignVerticalSpaceAroundIcon } from "lucide-svelte";

    export let currentImageName: string;
    export let promptOptionsByImage: Record<string, string[]>;
    export let imgInput: HTMLImageElement;

    export let setImage: (src: string) => void;
    export let setPrompt: (value: string) => void;
    export let setCurrentImage: (name: string) => void;
</script>

<button
    on:click={() => setCurrentImage("abstract")}
    on:click={() => setImage(abstractImage)}
    on:click={() => setPrompt(promptOptionsByImage["abstract"][0])}
>
    <img
        class="w-14 h-14 bg-gray"
        class:preview-active={imgInput?.src.includes(abstractImage)}
        src={abstractImage}
        alt="preview img abstract"
    />
</button>
<button
    on:click={() => setCurrentImage("beach")}
    on:click={() => setImage(beachImage)}
    on:click={() => setPrompt(promptOptionsByImage["beach"][0])}
>
    <img
        class="w-14 h-14 bg-gray"
        class:preview-active={imgInput?.src.includes(beachImage)}
        src={beachImage}
        alt="preview img beach"
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
