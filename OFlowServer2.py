"""
Optical flow frame interpolation server
"""
import copy
import logging
import base64
import cv2
import numpy as np
from fastapi import FastAPI
from io import BytesIO
from typing import List
from pydantic import BaseModel
import torch

log = logging.getLogger(__name__)

app = FastAPI()


def torch_image_show(image):
    """Show a torch image"""
    from PIL import Image
    import numpy as np

    if image.size().__len__() == 4:
        image = image[0]
    if image.dtype != torch.uint8:
        image = torch.mul(image, 255, )
        image = image.to(torch.uint8)  # Convert tensor to uint8 data type

    # must have at least 3 channels
    if image.shape[-1] == 1:
        image = torch.cat((image, image, image), dim=-1)

    image = image.numpy()
    try:
        image = Image.fromarray(image)  # Create a PIL image
    except TypeError as e:
        # this is a np array not a torch tensor
        # try to rearrange the channels using np
        image = np.moveaxis(image, 0, -1)

        # image.permute(1, 2, 0)
        image = Image.fromarray(image)  # Create a PIL image

    image.show()


class FrameInterpolationRequest(BaseModel):
    frame1: str
    frame2: str
    num_interp: int


def calculate_optical_flow(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Calculate dense optical flow between two frames using OpenCV."""
    if len(img1.shape) == 4:
        img1 = img1[0]

    if len(img2.shape) == 4:
        img2 = img2[0]
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

    flow = cv2.calcOpticalFlowFarneback(img1_gray, img2_gray, None, 0.25, 14, 16, 30, 9, 1.9, 0)
    # normalize to [-1, 1]
    old_center = flow.mean()
    flow = flow - old_center
    flow = flow - flow.min()
    old_scale = flow.max()
    flow = flow / old_scale
    flow = flow - 0.5
    flow = flow * 2
    flow = flow + (old_center / old_scale)
    return flow * 4


def warp_flow(img: np.ndarray, flow: np.ndarray) -> np.ndarray:
    """Warp a frame based on a flow field."""
    h, w = flow.shape[:2]
    flow[:, :, 0] += np.arange(w)
    flow[:, :, 1] += np.arange(h)[:, np.newaxis]
    warped = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return warped


def full_interpolate(frame1: np.ndarray, frame2: np.ndarray, percent: float,masked = 0.0) -> np.ndarray:
    """ Interpolate a single frame between two frames using optical flow."""
    flow = calculate_optical_flow(frame1, frame2)
    #flow[abs(flow) < masked] = 0
    # find the total amount of motion per pixel
    total_motion = np.sqrt(np.sum(flow ** 2, axis=-1))
    normalized_motion = total_motion / np.max(total_motion)
    masked_flow = flow * (normalized_motion < masked)[:, :, np.newaxis]
    #interpolated = warp_flow(frame1, flow * percent)
    interpolated = warp_flow(frame1, masked_flow * percent)
    return interpolated,flow


def interpolate_frames(frame1: np.ndarray, frame2: np.ndarray, num_interp: int) -> List[np.ndarray]:
    """Interpolate multiple frames between two frames using optical flow."""
    if len(frame1.shape) == 4:
        frame1 = frame1[0]

    if len(frame2.shape) == 4:
        frame2 = frame2[0]

    if num_interp > 1:
        interpolated = []
        flows = []
        left = copy.deepcopy(frame1)
        for i in range(num_interp):
            flow = calculate_optical_flow(left, frame2)
            flows.append(flow * ((i + .5) / num_interp))
            interpolated.append(warp_flow(left, flows[-1]))
            left = interpolated[-1]

    elif num_interp == 1:
        middle = (frame1 + frame2) / 2
        mid_left_linear = (frame1 + middle) / 2

        mid_left, f = full_interpolate(frame1, middle, 0.5,0.5)
        mid_right,_ = full_interpolate(middle, frame2, 0.5,0.5)
        m_lft_m_rgt,_ = full_interpolate(mid_left, mid_right, 0.5,0.5)

        #new_mid,_ = warp_flow(mid_left_linear, f * 0.5)
        new_mid = ((mid_right+mid_left)*.25)+(m_lft_m_rgt*.5)

    return [new_mid]


def frame_to_b64(frame: torch.tensor) -> str:
    """Encode a torch to base64 string."""
    mbuffer = BytesIO()
    torch.save(frame, mbuffer)
    mbytes = mbuffer.getvalue()
    b64_string = base64.b64encode(mbytes).decode()

    return b64_string


def b64_to_frame(b64_string: str) -> torch.Tensor:
    """Decode a base64 string to OpenCV frame."""
    mbytes = base64.b64decode(b64_string)
    mbuffer = BytesIO(mbytes)
    mtensor = torch.load(mbuffer)
    # make sure the tensor is (B, W, H, C)
    if len(mtensor.shape) == 3:
        mtensor.unsqueeze_(0)

    return mtensor


@app.post("/interpolate")
async def interpolate(request: FrameInterpolationRequest):
    frame1 = b64_to_frame(request.frame1)
    frame2 = b64_to_frame(request.frame2)
    # convert to numpy
    frame1 = frame1.numpy()
    frame2 = frame2.numpy()

    frames = interpolate_frames(frame1, frame2, request.num_interp)

    b64_frames = [frame_to_b64(f) for f in frames]
    return {"frames": b64_frames}


if __name__ == "__main__":
    hst = "127.0.0.1"
    log.info("Starting optical flow interpolation server")
    import uvicorn

    uvicorn.run("OFlowServer2:app", host=hst, port=8000, workers=8)
