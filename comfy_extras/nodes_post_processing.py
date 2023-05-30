import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

import comfy.utils


class Blend:
    def __init__(self):
        pass

    def add_alpha_channel(self,image: torch.Tensor):
        # add alpha channel but test first
        if image.shape[-1] != 4:
            print(f"adding alpha channel to image of shape {image.shape}")
            # add alpha channel
            image = torch.cat([image, torch.ones_like(image[..., :1])], dim=-1)
        return image

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "blend_factor": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
                "blend_mode": (["normal",
                                "multiply",
                                "screen",
                                "overlay",
                                "soft_light",
                                "white_to_alpha",
                                "composite_alpha"],),
            },
        }

    RETURN_TYPES = ("IMAGE","IMAGE")
    FUNCTION = "blend_images"

    CATEGORY = "image/postprocessing"

    def blend_images(self, image1: torch.Tensor, image2: torch.Tensor, blend_factor: float, blend_mode: str):
        """
        >>> img1 = torch.randn(6, 1, 1, 3)
        >>> img2 = torch.randn(1, 1, 1, 3)
        >>> blend_factor = 0.5
        >>> blend_mode = "white_to_alpha"
        >>> a = Blend().blend_images(img1, img2, blend_factor, blend_mode)
        img1 shape: torch.Size([6, 1, 1, 4])
        img2 shape: torch.Size([1, 1, 1, 4])
        >>> img1 = torch.randn(6, 1, 1, 3)
        >>> img2 = torch.randn(1, 1, 1, 3)
        >>> blend_factor = 0.5
        >>> blend_mode = "normal"
        >>> a = Blend().blend_images(img1, img2, blend_factor, blend_mode)
        img1 shape: torch.Size([6, 1, 1, 4])
        img2 shape: torch.Size([1, 1, 1, 4])
        """
        image1 = self.add_alpha_channel(image1)
        image2 = self.add_alpha_channel(image2)

        if image1.shape[1:3] != image2.shape[1:3]:
            # resize the smaller image to the size of the larger one
            im1size = image1.shape[-2]*image1.shape[-3]
            im2size = image2.shape[-2]*image2.shape[-3]
            if im1size > im2size:
                bigimg = image1
                smallimg = image2
            else:
                bigimg = image2
                smallimg = image1

            smallimg = smallimg.permute(0, 3, 1, 2)
            smallimg = comfy.utils.common_upscale(smallimg, bigimg.shape[2], bigimg.shape[1], upscale_method='bicubic',
                                                    crop='center')
            smallimg = smallimg.permute(0, 2, 3, 1)

            if im1size > im2size:
                image2 = smallimg
                image1 = bigimg
            else:
                image1 = smallimg
                image2 = bigimg

        blended_rgba_image = self.blend_mode(image1, image2, blend_mode)
        blended_rgba_image = self.add_alpha_channel(blended_rgba_image)
        blended_rgba_image = image1 * (1 - blend_factor) + blended_rgba_image * blend_factor
        blended_rgba_image = torch.clamp(blended_rgba_image, 0, 1)
        blended_image = blended_rgba_image[..., :3]
        return (blended_image,blended_rgba_image)

    def blend_mode(self, img1, img2, mode):
        """
        >>> img1 = torch.ones(6, 32, 32, 4)  # create a tensor with all ones
        >>> img1[:, 4:32-4, 4:32-4, 3] = 0.5  # create a transparent square in the middle
        >>> img1[:,  8:32- 8, 8:32- 8, 3] = 0.0  # inner is more transparent
        >>> img2 = torch.rand(1, 32, 32, 4) / 2  # create a tensor with values between 0 and 0.5
        >>> img2[:, :, :, 3] = 1.0  #
        >>> img2[:, 16:32, :, 3] = 0  #
        >>> blended_img = Blend().blend_mode(img1, img2, "composite_alpha")
        >>> blended_img.shape
        >>> display_image(blended_img,use_gimp=True)
        torch.Size([6, 4, 4, 4])
        >>> blended_img.shape
        torch.Size([6, 1, 1, 4])

        """
        print(f"img1 shape: {img1.shape}")
        print(f"img2 shape: {img2.shape}")
        if mode == "normal":
            return img2
        elif mode == "multiply":
            return img1 * img2
        elif mode == "screen":
            return 1 - (1 - img1) * (1 - img2)
        elif mode == "overlay":
            return torch.where(img1 <= 0.5, 2 * img1 * img2, 1 - 2 * (1 - img1) * (1 - img2))
        elif mode == "soft_light":
            return torch.where(img2 <= 0.5, img1 - (1 - 2 * img2) * img1 * (1 - img1),
                               img1 + (2 * img2 - 1) * (self.g(img1) - img1))
        elif mode == "composite_alpha":
            print(f"beginning of composite_alpha")
            print(f"img1 shape: {img1.shape}")
            print(f"img2 shape: {img2.shape}")
            # alpha blending
            alpha_channel = img1[:, :, :, 3:4]
            img2_contribution = img2 * (1-alpha_channel)
            img1_contribution = img1 * alpha_channel
            out = img2_contribution + img1_contribution
            return out


        elif mode == "white_to_alpha":
            new_alpha_values = img2[:, :, :, 0:1]
            if img1.shape[0] != img2.shape[0]:
                alpha_channel = new_alpha_values.repeat(img1.shape[0], 1, 1, 1)
            else:
                alpha_channel = new_alpha_values
            # print (f"alpha_channel shape: {alpha_channel.shape}")
            # print (f"img2 shape: {img2.shape}")
            # set the alpha channel of img1 to the new alpha values
            out = torch.cat([img1[:, :, :, 0:3], alpha_channel], dim=-1)
            return out

        else:
            raise ValueError(f"Unsupported blend mode: {mode}")

    def g(self, x):
        return torch.where(x <= 0.25, ((16 * x - 12) * x + 4) * x, torch.sqrt(x))

def gaussian_kernel(kernel_size: int, sigma: float):
    x, y = torch.meshgrid(torch.linspace(-1, 1, kernel_size), torch.linspace(-1, 1, kernel_size), indexing="ij")
    d = torch.sqrt(x * x + y * y)
    g = torch.exp(-(d * d) / (2.0 * sigma * sigma))
    return g / g.sum()

class Blur:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "blur_radius": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 31,
                    "step": 1
                }),
                "sigma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "blur"

    CATEGORY = "image/postprocessing"

    def blur(self, image: torch.Tensor, blur_radius: int, sigma: float):
        if blur_radius == 0:
            return (image,)

        batch_size, height, width, channels = image.shape

        kernel_size = blur_radius * 2 + 1
        kernel = gaussian_kernel(kernel_size, sigma).repeat(channels, 1, 1).unsqueeze(1)

        image = image.permute(0, 3, 1, 2)  # Torch wants (B, C, H, W) we use (B, H, W, C)
        padded_image = F.pad(image, (blur_radius,blur_radius,blur_radius,blur_radius), 'reflect')
        blurred = F.conv2d(padded_image, kernel, padding=kernel_size // 2, groups=channels)[:,:,blur_radius:-blur_radius, blur_radius:-blur_radius]
        blurred = blurred.permute(0, 2, 3, 1)

        return (blurred,)


class Quantize:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "colors": ("INT", {
                    "default": 256,
                    "min": 1,
                    "max": 256,
                    "step": 1
                }),
                "dither": (["none", "floyd-steinberg"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "quantize"

    CATEGORY = "image/postprocessing"

    def quantize(self, image: torch.Tensor, colors: int = 256, dither: str = "FLOYDSTEINBERG"):
        batch_size, height, width, _ = image.shape
        result = torch.zeros_like(image)

        dither_option = Image.Dither.FLOYDSTEINBERG if dither == "floyd-steinberg" else Image.Dither.NONE

        for b in range(batch_size):
            tensor_image = image[b]
            img = (tensor_image * 255).to(torch.uint8).numpy()
            pil_image = Image.fromarray(img, mode='RGB')

            palette = pil_image.quantize(
                colors=colors)  # Required as described in https://github.com/python-pillow/Pillow/issues/5836
            quantized_image = pil_image.quantize(colors=colors, palette=palette, dither=dither_option)

            quantized_array = torch.tensor(np.array(quantized_image.convert("RGB"))).float() / 255
            result[b] = quantized_array

        return (result,)


class Sharpen:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "sharpen_radius": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 31,
                    "step": 1
                }),
                "sigma": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                }),
                "alpha": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 5.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "sharpen"

    CATEGORY = "image/postprocessing"

    def sharpen(self, image: torch.Tensor, sharpen_radius: int, sigma:float, alpha: float):
        if sharpen_radius == 0:
            return (image,)

        batch_size, height, width, channels = image.shape

        kernel_size = sharpen_radius * 2 + 1
        kernel = gaussian_kernel(kernel_size, sigma) * -(alpha*10)
        center = kernel_size // 2
        kernel[center, center] = kernel[center, center] - kernel.sum() + 1.0
        kernel = kernel.repeat(channels, 1, 1).unsqueeze(1)

        tensor_image = image.permute(0, 3, 1, 2)  # Torch wants (B, C, H, W) we use (B, H, W, C)
        tensor_image = F.pad(tensor_image, (sharpen_radius,sharpen_radius,sharpen_radius,sharpen_radius), 'reflect')
        sharpened = F.conv2d(tensor_image, kernel, padding=center, groups=channels)[:,:,sharpen_radius:-sharpen_radius, sharpen_radius:-sharpen_radius]
        sharpened = sharpened.permute(0, 2, 3, 1)

        result = torch.clamp(sharpened, 0, 1)

        return (result,)


NODE_CLASS_MAPPINGS = {
    "ImageBlend": Blend,
    "ImageBlur": Blur,
    "ImageQuantize": Quantize,
    "ImageSharpen": Sharpen,
}

print(f"entering {__name__}")
print(f"Registered {len(NODE_CLASS_MAPPINGS)} image nodes.")

if __name__ == "__main__":
    pass
else:

    try:
        import comfy.utils
        def my_logger(*args):
            with open("log.txt", "a") as f:
                f.write(str(args) + "\n")
                old_print(*args)
        old_print = print
        print = lambda x: my_logger(x)
    except:
        pass
