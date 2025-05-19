from pathlib import Path

import modal
from fastapi import FastAPI, File, Form, Response, UploadFile
from fastapi.staticfiles import StaticFiles

app = modal.App("stable-diffusion-xl-turbo")

assets_path = Path(__file__).parent / "dist"

web_image = (
    modal.Image.debian_slim()
    .pip_install("jinja2", "fastapi[standard]")
    .add_local_dir(assets_path, "/assets")
)


def download_weights():
    from huggingface_hub import snapshot_download

    # Ignore files that we don't need to speed up download time.
    ignore = [
        "*.bin",
        "*.onnx_data",
        "*/diffusion_pytorch_model.safetensors",
    ]

    snapshot_download("stabilityai/sdxl-turbo", ignore_patterns=ignore)

    # https://huggingface.co/docs/diffusers/main/en/using-diffusers/sdxl_turbo#speed-up-sdxl-turbo-even-more
    # vae is used for a inference speedup
    snapshot_download("madebyollin/sdxl-vae-fp16-fix", ignore_patterns=ignore)


inference_image = (
    modal.Image.debian_slim()
    .pip_install(
        "Pillow~=10.1.0",
        "diffusers~=0.24",
        "transformers~=4.35",
        "accelerate~=0.25",
        "safetensors~=0.4",
        "fastapi[standard]",
    )
    .run_function(download_weights)
)

with inference_image.imports():
    from io import BytesIO

    import torch
    from diffusers import AutoencoderKL, AutoPipelineForImage2Image
    from diffusers.utils import load_image
    from PIL import Image


@app.cls(
    gpu="A100",
    image=inference_image,
    scaledown_window=240,
    max_containers=10,
)
class Model:
    @modal.enter()
    def enter(self):
        self.pipe = AutoPipelineForImage2Image.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16,
            device_map="balanced",
            variant="fp16",
            vae=AutoencoderKL.from_pretrained(
                "madebyollin/sdxl-vae-fp16-fix",
                torch_dtype=torch.float16,
                device_map="balanced",
            ),
        )

        # We execute a blank inference since there are objects that are lazily loaded that
        # we want to start loading before an actual user query
        self.pipe(
            "blank",
            image=Image.new("RGB", (800, 1280), (255, 255, 255)),
            num_inference_steps=1,
            strength=1,
            guidance_scale=0.0,
            seed=42,
        )

    @modal.fastapi_endpoint(method="POST")
    async def inference(
        self,
        image: UploadFile = File(...),
        prompt: str = Form(...),
        num_iterations: str = Form(...),
    ):
        img_data_in = await image.read()

        init_image = load_image(Image.open(BytesIO(img_data_in))).resize((512, 512))
        # based on trial and error we saw the best results with 3 inference steps
        # it had better generation results than 4,5,6 even though it's faster
        num_inference_steps = int(num_iterations)
        # note: anything under 0.5 strength gives blurry results
        strength = 0.999 if num_iterations == 2 else 0.65
        assert num_inference_steps * strength >= 1

        image = self.pipe(
            prompt,
            image=init_image,
            num_inference_steps=num_inference_steps,
            strength=strength,
            guidance_scale=0.0,
            seed=42,
        ).images[0]

        byte_stream = BytesIO()
        image.save(byte_stream, format="jpeg")
        img_data_out = byte_stream.getvalue()

        return Response(content=img_data_out, media_type="image/jpeg")


@app.function(image=web_image)
@modal.concurrent(max_inputs=10)
@modal.asgi_app()
def fastapi_app():
    import jinja2

    web_app = FastAPI()

    with open("/assets/index.html", "r") as f:
        template_html = f.read()

    template = jinja2.Template(template_html)

    with open("/assets/index.html", "w") as f:
        # Mount the {{ inference_url }} with the Modal inference endpoint.
        html = template.render(inference_url=Model.inference.web_url)
        f.write(html)

    web_app.mount("/", StaticFiles(directory="/assets", html=True))

    return web_app
