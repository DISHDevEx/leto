#!/usr/bin/env python
import torch

# A cache to store precomputed grids
objBackwarpcache = {}


def backwarp(tenIn: torch.Tensor, tenFlow: torch.Tensor):
    """
    Backwarp an input tensor using optical flow.

    Args:
        tenIn (torch.Tensor): The input tensor to warp.
        tenFlow (torch.Tensor): The optical flow tensor.

    Returns:
        torch.Tensor: The warped input tensor.
    """
    if (
        "grid"
        + str(tenFlow.dtype)
        + str(tenFlow.device)
        + str(tenFlow.shape[2])
        + str(tenFlow.shape[3])
        not in objBackwarpcache
    ):
        tenHor = (
            torch.linspace(
                start=-1.0,
                end=1.0,
                steps=tenFlow.shape[3],
                dtype=tenFlow.dtype,
                device=tenFlow.device,
            )
            .view(1, 1, 1, -1)
            .repeat(1, 1, tenFlow.shape[2], 1)
        )
        tenVer = (
            torch.linspace(
                start=-1.0,
                end=1.0,
                steps=tenFlow.shape[2],
                dtype=tenFlow.dtype,
                device=tenFlow.device,
            )
            .view(1, 1, -1, 1)
            .repeat(1, 1, 1, tenFlow.shape[3])
        )

        objBackwarpcache[
            "grid"
            + str(tenFlow.dtype)
            + str(tenFlow.device)
            + str(tenFlow.shape[2])
            + str(tenFlow.shape[3])
        ] = torch.cat([tenHor, tenVer], 1)

    if tenFlow.shape[3] == tenFlow.shape[2]:
        tenFlow = tenFlow * (2.0 / ((tenFlow.shape[3] and tenFlow.shape[2]) - 1.0))
    elif tenFlow.shape[3] != tenFlow.shape[2]:
        tenFlow = tenFlow * torch.tensor(
            data=[2.0 / (tenFlow.shape[3] - 1.0), 2.0 / (tenFlow.shape[2] - 1.0)],
            dtype=tenFlow.dtype,
            device=tenFlow.device,
        ).view(1, 2, 1, 1)

    return torch.nn.functional.grid_sample(
        input=tenIn,
        grid=(
            objBackwarpcache[
                "grid"
                + str(tenFlow.dtype)
                + str(tenFlow.device)
                + str(tenFlow.shape[2])
                + str(tenFlow.shape[3])
            ]
            + tenFlow
        ).permute(0, 2, 3, 1),
        mode="bilinear",
        padding_mode="zeros",
        align_corners=True,
    )
