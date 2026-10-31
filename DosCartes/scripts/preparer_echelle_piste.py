#!/usr/bin/env python3
"""Extrait la piste d’or (pièces + ruban) d’EchelleOr.png sur fond transparent.

Sortie à la racine du dépôt :
- EchelleOr_piste.png         750×1050 RGBA
- EchelleOr_piste_apercu.png  même image sur damier
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from separer_logos_fonds import decontam, preview_checker

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[1]
SRC = REPO / "EchelleOr.png"


def largest_cc(mask: np.ndarray) -> np.ndarray:
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if n <= 1:
        return mask.astype(np.uint8)
    return (labels == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)


def fill_holes(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    inv = (mask == 0).astype(np.uint8)
    flood = inv.copy()
    m = np.zeros((h + 2, w + 2), np.uint8)
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv2.floodFill(flood, m, seed, 2)
    out = mask.copy()
    out[flood == 1] = 1
    return out


def gold_mask(rgb: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.int32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
    return (
        (H >= 14)
        & (H <= 38)
        & (S > 90)
        & (V > 70)
        & (r > 130)
        & (r > g)
        & (r > b + 25)
        & ~((V > 200) & (H < 20) & (r > 200))
    ).astype(np.uint8)


def extract_piste(rgb: np.ndarray) -> np.ndarray:
    h, w = rgb.shape[:2]
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    gold = gold_mask(rgb)

    core = cv2.morphologyEx(gold, cv2.MORPH_CLOSE, k5, iterations=1)
    core = largest_cc(core)
    core = cv2.morphologyEx(core, cv2.MORPH_OPEN, k5, iterations=1)
    core = largest_cc(core)
    core = cv2.morphologyEx(core, cv2.MORPH_CLOSE, k5, iterations=2)
    filled = fill_holes(core)

    circles = cv2.HoughCircles(
        filled * 255,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=55,
        param1=40,
        param2=18,
        minRadius=28,
        maxRadius=80,
    )
    if circles is None:
        raise RuntimeError("aucune pièce détectée")
    circs = np.round(circles[0]).astype(int)
    if len(circs) < 10:
        raise RuntimeError(f"trop peu de pièces ({len(circs)})")

    pts = circs[:, :2].astype(float)
    n = len(pts)
    dist = np.linalg.norm(pts[:, None] - pts[None, :], axis=2)
    used = {0}
    edges: list[tuple[int, int]] = []
    while len(used) < n:
        best = None
        for i in used:
            for j in range(n):
                if j in used:
                    continue
                if best is None or dist[i, j] < best[0]:
                    best = (dist[i, j], i, j)
        assert best is not None
        edges.append((best[1], best[2]))
        used.add(best[2])

    cx0, cy0 = w / 2, h / 2
    ic = int(np.argmin(np.hypot(circs[:, 0] - cx0, circs[:, 1] - cy0)))

    prior = np.zeros((h, w), np.uint8)
    for i, (cx, cy, cr) in enumerate(circs):
        rad = int(cr) + (2 if i == ic else 1)
        cv2.circle(prior, (int(cx), int(cy)), rad, 1, -1)
    for i, j in edges:
        cv2.line(
            prior,
            (int(circs[i, 0]), int(circs[i, 1])),
            (int(circs[j, 0]), int(circs[j, 1])),
            1,
            28,
        )
    prior = cv2.dilate(prior, k5, iterations=1)

    keep = ((gold | filled) & prior).astype(np.uint8)
    for i, (cx, cy, cr) in enumerate(circs):
        cv2.circle(keep, (int(cx), int(cy)), int(cr) + (2 if i == ic else 1), 1, -1)
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, k3, iterations=1)
    keep = fill_holes(keep)
    keep = (keep & cv2.dilate(prior, k5, iterations=3)).astype(np.uint8)
    keep = largest_cc(keep)

    halo = cv2.dilate(keep, k3, iterations=1)
    alpha = np.zeros((h, w), np.uint8)
    alpha[keep == 1] = 255
    alpha[(halo == 1) & (keep == 0)] = 64
    return decontam(np.dstack([rgb, alpha]), (16, 22, 30))


def main() -> None:
    rgb = np.asarray(Image.open(SRC).convert("RGB"))
    rgba = extract_piste(rgb)
    dest = REPO / "EchelleOr_piste.png"
    Image.fromarray(rgba).save(dest, "PNG")
    preview_checker(rgba).save(REPO / "EchelleOr_piste_apercu.png", "PNG")
    print("piste", dest.name, rgba.shape, "opaque", int((rgba[..., 3] == 255).sum()))


if __name__ == "__main__":
    main()
