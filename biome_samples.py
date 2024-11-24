from PIL import Image, ImageOps
from skimage.color import rgb2luv, luv2rgb
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import numpy as np
import sys

grasses = [
    'grass_block_top.png',
    'short_grass.png',
    'tall_grass_top.png',
    'fern.png',
    'large_fern_top.png']
foliages = [
    'oak_leaves.png',
    'jungle_leaves.png',
    'acacia_leaves.png',
    'dark_oak_leaves.png',
    'mangrove_leaves.png',
    'vine.png']

def to_rgb(s):
    return np.asarray([int(s[i+1:i+3], 16) / 255 for i in (0,2,4)])

def to_hex(rgb):
    rgb = [round(c * 255) for c in rgb]
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

class Color:
    def __init__(self, weight, rgb, multiplier = 1.0):
        self.weight = weight
        self.rgb = np.asarray(rgb) * multiplier
        self.luv = rgb2luv(self.rgb)

    def __repr__(self):
        return '{{{}x#{}}}'.format(self.weight, to_hex(self.rgb))

    def modified(self, col):
        #col = np.multiply(self.rgb, col)
        col = np.clip(self.luv[0] * 0.01 * col, 0, 1)
        return Color(self.weight, col)


class Biome:
    def __init__(self):
        self.id = -1
        self.luv = ()
        self.bounds = []
        self.space = None
        self.path = []
    
    def setup(self, lines, assetpath):
        self.id = int(lines[0])
        icons = []
        grass1 = grass2 = foliage = water = None
        for rc in lines[1:]:
            if rc.startswith('G#'):
                grass1 = to_rgb(rc[1:])
            elif rc.startswith('H#'):
                grass2 = to_rgb(rc[1:])
            elif rc.startswith('F#'):
                foliage = to_rgb(rc[1:])
            elif rc.startswith('W#'):
                water = to_rgb(rc[1:])
            else:
                if ' ' in rc:
                    w = float(rc.split(' ')[0])
                    rc = rc.split(' ')[1]
                else:
                    w = 1
                im = Image.open(assetpath + '/' + rc)
                im = im.convert("RGBA").crop((0,0, 16,16))
                # extract the non transparent colors
                cols = [Color(c[0] * w, c[1][:-1], 1/255) for c in im.getcolors() if c[1][3] != 0]
                # transparency on leaves appears almost black due to lighting
                if 'leaves' in rc:
                    cols += [Color(c[0] * w, (0,0,0)) for c in im.getcolors() if c[1][3] == 0]
                mod = None
                if rc in grasses:
                    mod = grass1
                    if grass2 is not None:
                        icons.append([c.modified(grass2) for c in cols])
                        w /= 2
                elif rc in foliages:
                    mod = foliage
                elif rc == 'water_overlay.png':
                    mod = water
                elif rc == 'birch_leaves.png':
                    mod = to_rgb('#80A755')
                elif rc == 'spruce_leaves.png':
                    mod = to_rgb('#619961')
                elif rc == 'lily_pad.png':
                    mod = to_rgb('#208030')
                if mod is not None:
                    icons.append([c.modified(mod) for c in cols])
                else:
                    icons.append(cols)
        # build the weighted average color
        total = np.zeros(3)
        weight = 0
        bounds = set()
        for cols in icons:
            for c in cols:
                total += c.luv * c.weight
                weight += c.weight
                bounds.add(tuple(c.luv))
        self.luv = total / weight
        # construct the interpolatable color space
        self.bounds = list(bounds)
        self.space = Delaunay(self.bounds)
        return self

    def create_variant(self, biome, dlight):
        dluv = (dlight, 0, 0)
        b = Biome()
        b.id = biome
        b.luv = self.luv + dluv
        b.bounds = [c + dluv for c in self.bounds]
        b.space = Delaunay(self.bounds)
        b.path = []
        return b


def load(path, assetpath):
    biomes = dict()
    with open(path) as f:
        lines = []
        for l in f:
            l = l[:-1]
            if not l:
                if lines:
                    name = lines[0]
                    biomes[name] = Biome().setup(lines[1:], assetpath)
                    lines = []
                continue
            lines.append(l)

    # some variants are too similar to distinguish by block samples
    hills = -3.5
    modified = 3.5
    
    # Note:
    # tall_birch_forest               = birch_forest+128,
    # tall_birch_hills                = birch_forest_hills+128,
    # old_growth_birch_forest         = tall_birch_forest,
    # -> birch_forest + hills ; tall_birch_forest + hills
    # and
    # shattered_savanna               = savanna+128,
    # shattered_savanna_plateau       = savanna_plateau+128,
    # windswept_savanna               = shattered_savanna,
    # -> savanna + modified ; windswept_savanna + modified
    biomes['snowy_mountains'] = biomes['snowy_plains'].create_variant(13, hills)
    biomes['desert_hills'] = biomes['desert'].create_variant(17, hills)
    biomes['wooded_hills'] = biomes['forest'].create_variant(18, hills)
    biomes['taiga_hills'] = biomes['taiga'].create_variant(19, hills)
    biomes['jungle_hills'] = biomes['jungle'].create_variant(22, hills)
    biomes['birch_forest_hills'] = biomes['birch_forest'].create_variant(28, hills)
    biomes['snowy_taiga_hills'] = biomes['snowy_taiga'].create_variant(31, hills)
    biomes['giant_tree_taiga_hills'] = biomes['old_growth_pine_taiga'].create_variant(33, hills)
    biomes['savanna_plateau'] = biomes['savanna'].create_variant(36, modified)
    biomes['desert_lakes'] = biomes['desert'].create_variant(130, modified)
    biomes['taiga_mountains'] = biomes['taiga'].create_variant(133, hills * 2)
    biomes['swamp_hills'] = biomes['swamp'].create_variant(134, hills)
    biomes['modified_jungle'] = biomes['jungle'].create_variant(149, modified)
    biomes['modified_jungle_edge'] = biomes['sparse_jungle'].create_variant(151, modified)
    biomes['tall_birch_hills'] = biomes['old_growth_birch_forest'].create_variant(156, hills)
    biomes['dark_forest_hills'] = biomes['dark_forest'].create_variant(157, hills)
    biomes['snowy_taiga_mountains'] = biomes['snowy_taiga'].create_variant(158, hills)
    biomes['giant_spruce_taiga_hills'] = biomes['old_growth_spruce_taiga'].create_variant(161, hills)
    biomes['modified_gravelly_mountains'] = biomes['windswept_gravelly_hills'].create_variant(162, modified)
    biomes['modified_wooded_badlands_plateau'] = biomes['wooded_badlands'].create_variant(166, modified)
    biomes['modified_badlands_plateau'] = biomes['badlands_plateau'].create_variant(167, modified)
    biomes['bamboo_jungle_hills'] = biomes['bamboo_jungle'].create_variant(169, hills)
    biomes['shattered_savanna_plateau'] = biomes['windswept_savanna'].create_variant(164, modified)

    return biomes


def gradient(biomes, b1):
    luv = biomes[b1].luv
    total = np.zeros(3)
    for b2 in biomes.keys():
        if b1 == b2:
            continue
        # determine difference of colors, giving more importance to lightness
        l,u,v = d = luv - biomes[b2].luv
        w = 4*l*l + u*u + v*v
        total += d / (0.01 + w)
    return total

def optimize(biomes):
    for name,b in biomes.items():
        b.grad = gradient(biomes, name)
    step = 0.25 / max(np.linalg.norm(b.grad) for b in biomes.values())
    for b in biomes.values():
        new = b.luv + b.grad * step
        # only allow changes that interpolate between the sample colors
        if b.space.find_simplex(new) >= 0:
            b.path.append(tuple(b.luv))
            b.luv = new

def plot(biomes):
    n = len(biomes)
    cols = [luv2rgb(b.luv) for b in biomes.values()]
    L = [b.luv[0] for b in biomes.values()]
    U = [b.luv[1] for b in biomes.values()]
    V = [b.luv[2] for b in biomes.values()]

    #plt.style.use('dark_background')
    ax = plt.figure().add_subplot(111, projection='3d')
    ax.scatter(L, U, V, s=28, c=[(0,0,0)]*n, lw=0)
    ax.scatter(L, U, V, s=24, c=cols, lw=0)

    for i,b in enumerate(biomes.values()):
        if len(b.path):
            c = luv2rgb(b.path[0])
            l = [p[0] for p in b.path]
            u = [p[1] for p in b.path]
            v = [p[2] for p in b.path]
            ax.plot(l, u, v, linewidth=1.25, color=(0,0,0))
            ax.plot(l, u, v, linewidth=1.0, color=c)
        ax.text(L[i], U[i], V[i], b.id)

    ax.set_xlabel('L')
    ax.set_ylabel('u')
    ax.set_zlabel('v')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.show()


if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print ('usage: biome_samples.py <BLOCK_ASSET_DIR> <OPTIMIZATION_STEPS>')
        sys.exit(0)

    biomes = load('biome_blocks.txt', sys.argv[1])

    for i in range(int(sys.argv[2])):
        optimize(biomes)

    for name in sorted(biomes.keys()):
        print (name, to_hex(luv2rgb(biomes[name].luv)))

    plot(biomes)




