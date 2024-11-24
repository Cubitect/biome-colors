# Biome Colors from Block Samples

Many Minecraft biome mapping tools currently use colormaps that are based on the [AMIDST project](https://github.com/toolbox4minecraft/amidst),
which has not been updated to the 1.18 world generation. Also there is not a clear, systematic method of expanding AMIDST's colormap,
as the colors are only vaguely based on the in-game appearance of the biomes.
Because of this, projects have diverged with the colormaps they use.

This repo makes an attempt to create a new biome colormap that is based on the characteristic blocks that can be found in those biomes.

The results can be seen in [sampled_colormap.txt](sampled_colormap.txt) and [sampled_colormap_optimized.txt](sampled_colormap_optimized.txt),
and can be loaded in [Cubiomes Viewer](https://github.com/Cubitect/cubiomes-viewer).


## Generation Process

The selection of sampled blocks and their contributions is specified in [biome_blocks.txt](biome_blocks.txt)
and was inspired by the [Minecraft Wiki](https://minecraft.wiki/w/Biome) page for each biome.
The contribution factor for each block is loosely based on the abundance of the blocks in that biome.
However, the values are a degree of freedom that I've often adjusted to achive certain results.

The biome color is then determined by a weighted average (the mean value in the [CIELUV](https://en.wikipedia.org/wiki/CIELUV) colorspace)
of the sample colors. Some of the biome variants have a block palette that is too similar to the main biome to use this process,
and instead apply a small offset in lightness to the main biome color.

After the average colors are detemined, the contrast between some of the biomes may be a little low.
To improve open this, one can apply optimization passes, which nudge the biome colors so that they become more distinct.
This movement is constrained to the interpolated colorspace of the sample colors.


## Running the Script

To generate the colors yourself, you first need to extract the block assests folder from a Minecraft Java Client.
These are located at `/assets/minecraft/textures/block` inside the Minecraft Jar-File (1.21.3).

You can then run the `biome_samples.py` script, specifying the directory of the block assets as the first argument and the number of color-optimization passes you want to apply as the second argument.

E.g.:
```bash
biomes_samples.py ./block/ 50
```

