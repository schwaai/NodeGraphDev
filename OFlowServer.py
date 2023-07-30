import aiohttp
import asyncio

import numpy
from fastapi import FastAPI
from numpy import arange
from pydantic import BaseModel
import numpy as np
import torch
import cv2
import uvicorn
from multiprocessing import Process
import requests
import time
import base64
from io import BytesIO


class Tensor(BaseModel):
    data: list
    shape: list
    dtype: str


app = FastAPI()

from numba import jit


def calculate_optical_flow(img1, img2):
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    # CalcOpticalFlowFarneback(
    #     InputArray prev, InputArray next, InputOutputArray flow, double pyrScale,
    # int levels, int winsize,
    # iterations,
    # polyN,
    # polySigma,
    # OpticalFlowFlags

    # )
    flow = cv2.calcOpticalFlowFarneback(img1_gray, img2_gray, None, 0.25, 14, 16, 30, 9, 1.9, 0)
    # normalize to [-1, 1]
    flow = flow - flow.min()
    flow = flow / flow.max()
    flow = flow - 0.5
    flow = flow * 2
    return flow


def warp_flow(img, flow):
    # height, width,_ = flow.shape
    # R2 = np.dstack(np.meshgrid(np.arange(width), np.arange(height)))
    # pixel_map = R2 + flow
    # res = cv2.remap(img, pixel_map, None, cv2.INTER_LINEAR)
    h, w = flow.shape[:2]
    flow = -flow
    flow[:, :, 0] += np.arange(w)
    flow[:, :, 1] += np.arange(h)[:, np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LANCZOS4)
    return res


def interpolate_frames(frame1, frame2):
    flow = calculate_optical_flow(frame1, frame2)
    frame_interpolated = warp_flow(frame1, flow * 0.5)
    return frame_interpolated


class FrameInterpolationRequest(BaseModel):
    tensor1: str
    tensor2: str
    num_interpolations: int  # Number of frames to interpolate
    factor: float = 10.0  # Factor to scale the optical flow by


# @jit(nopython=False)
def interpolate_frames_torch(frames, num_interpolations, factor=1.0):
    # def interpolate_frames_torch_recursive(frames, num_interpolations, factor=1.0):
    frames = frames.cpu().numpy()  # Convert to numpy array
    from copy import deepcopy
    right_frames = []
    left_frames = []
    all_places = []

    frame1, frame2 = frames[0], frames[1]

    p_per_frame = 1 / (num_interpolations + 1)
    left = deepcopy(frame1)
    for percent in arange(p_per_frame, 1, p_per_frame):
        ip = 1- percent
        left = (left * ip) + (frame2 * percent)
        flow = calculate_optical_flow(left, frame2)
        left = warp_flow(left, flow * percent * factor)
        left_frames.append(left)

    #p_per_frame = 1 / (num_interpolations + 1)
    #right = deepcopy(frame2)
    #for percent in arange(1, 0, -p_per_frame):
    #    flow = calculate_optical_flow(right, frame1)
    #    right = warp_flow(right, flow * percent * factor)
    #    right_frames.append(right)
    # Combine the frames
    #interpolated_frames = []
    #right_frames.reverse()
    #for i in range(len(left_frames)):
    #    tmp = (left_frames[i] + right_frames[i]) / 2
    #    interpolated_frames.append(tmp)

    #return interpolated_frames
    return left_frames


@app.post("/interpolate")
async def interpolate(request: FrameInterpolationRequest):
    frame1 = torch.load(BytesIO(base64.b64decode(request.tensor1)))
    frame2 = torch.load(BytesIO(base64.b64decode(request.tensor2)))

    frames = torch.cat([frame1, frame2])
    factor = request.factor
    interpolated_frames: list[numpy.ndarray] = interpolate_frames_torch(
        frames,
        request.num_interpolations,
        factor=factor,
    )

    # Convert to tensors and encode as base64
    encoded_frames = []
    for frame in interpolated_frames:
        tensor = torch.from_numpy(frame)
        buffer = BytesIO()
        torch.save(tensor, buffer)
        encoded_tensor = base64.b64encode(buffer.getvalue()).decode('utf-8')
        encoded_frames.append(encoded_tensor)

    return {"interpolated_frames": encoded_frames}


import uvicorn
import time
import requests
import os
import pathlib
import subprocess

hst = "127.0.0.1"


async def send_request(session, url, tensor1_bytes, tensor2_bytes, num_interpolations):
    async with session.post(url,
                            json={"tensor1": tensor1_bytes,
                                  "tensor2": tensor2_bytes,
                                  "num_interpolations": num_interpolations}
                            ) as response:
        json_response = await response.json()
        return json_response


def run_server():
    # Get the directory of the current script file
    script_directory = pathlib.Path(__file__).parent.absolute()
    # Change the current working directory to the script directory
    os.chdir(script_directory)
    # Start the server
    uvicorn.run("OFlowServer:app", host=hst, port=8000, workers=4)


from PIL import Image, ImageSequence


def get_random_tensor_image():
    # random 256x256x3 tensor
    tensor = torch.rand(1, 256, 256, 3)
    return tensor

    # Convert tensors to bytes a


async def t_server(t1, t2, num_interpolations):
    # Get the directory of the current script file
    script_directory = pathlib.Path(__file__).parent.absolute()
    # Change the current working directory to the script directory
    os.chdir(script_directory)

    # random 256x256x3 tensor
    tensor1 = t1
    tensor2 = t2

    # Convert tensors to bytes and encode as base64
    buffer = BytesIO()
    torch.save(tensor1, buffer)
    tensor1_bytes = base64.b64encode(buffer.getvalue()).decode('utf-8')

    buffer = BytesIO()
    torch.save(tensor2, buffer)
    tensor2_bytes = base64.b64encode(buffer.getvalue()).decode('utf-8')

    async with aiohttp.ClientSession() as session:
        tasks = []
        url = f"http://{hst}:8000/interpolate"
        tasks.append(send_request(session, url, tensor1_bytes, tensor2_bytes, num_interpolations))
        responses = await asyncio.gather(*tasks)

    tensors = []
    for response in responses:
        for frame in response["interpolated_frames"]:
            # Convert the base64-encoded tensor back to a tensor
            buffer = BytesIO(base64.b64decode(frame))
            tensor = torch.load(buffer)
            tensors.append(tensor)

    return tensors


def tensors_to_gif(tensors):
    images = []
    for tensor in tensors:
        # Convert the tensor to an image
        np_img = np.array(tensor) * 255
        image = Image.fromarray(np_img.astype(np.uint8))
        images.append(image)

    # Create an animated GIF
    images[0].save('animated.gif', save_all=True, append_images=images[1:], optimize=False, duration=40, loop=1)

    # Open the animated GIF using the default image viewer on Windows
    subprocess.Popen(['start', 'animated.gif'], shell=True)


import asyncio
import os
import pathlib
from multiprocessing import Process

import torch
from PIL import Image


def create_moving_block_images_rgb(image_size, block_size, displacement):
    # Create an image with a block of pixels
    img1 = torch.zeros((image_size, image_size, 3))
    start_point = image_size // 2 - block_size // 2
    img1[start_point:start_point + block_size, start_point:start_point + block_size, :] = 1.0

    # Create a second image where the block has moved
    img2 = torch.zeros((image_size, image_size, 3))
    img2[start_point + displacement:start_point + block_size + displacement,
    start_point + displacement:start_point + block_size + displacement, :] = 1.0

    # Add an extra dimension for the batch
    img1 = img1.unsqueeze(0)
    img2 = img2.unsqueeze(0)

    return img1, img2


async def main():
    script_directory = pathlib.Path(__file__).parent.absolute()
    # Change the current working directory to the script directory
    os.chdir(script_directory)
    # Start server in a separate process
    run_server()
    #server_process = Process(target=run_server)
    #server_process.start()


async def long_test():
    await asyncio.sleep(10)

    # Run tests
    # t1,t2 = create_moving_block_images_rgb(256,64,8)
    t1 = get_random_tensor_image()
    t2 = get_random_tensor_image()

    t3 = await t_server(t1, t2, 10)
    # make pairs
    pairs = zip(t3[::2], t3[1::2])
    # now make tasks from the pairs
    tasks = []
    from copy import deepcopy
    async def create_task(a, b):
        return await t_server(a, b, 50)

    for a, b in pairs:
        a = a.unsqueeze(0)
        b = b.unsqueeze(0)
        aa = deepcopy(a)
        bb = deepcopy(b)
        tasks.append(asyncio.create_task(create_task(aa, bb)))

    # await the tasks
    tensors = await asyncio.gather(*tasks)
    # flatten the list
    out = []
    for i in tensors:
        out += i  # This concatenates the lists, maintaining the order of elements within each list.
    tensors = out
    tensors_to_gif(tensors)


if __name__ == "__main__":
    asyncio.run(main())
