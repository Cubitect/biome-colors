# Biome Colors from Block Samples

Many Minecraft biome mapping tools currently use colormaps that are based on the [AMIDST project](https://github.com/toolbox4minecraft/amidst),
which has not been updated to the 1.18 world generation, and there isn't a clear, systematic method of expanding the colormap,
since the colors are not directly based on the in-game appearance of the biomes.
Because of this, projects have diverged with the colormaps they use.

This repo makes an attempt to create a new biome colormap that is based on the characteristic blocks that can be found in those biomes.


## Progress

The current results are saved in [sampled_colormap.txt](sampled_colormap.txt) and [sampled_colormap_optimized.txt](sampled_colormap_optimized.txt),
and can be loaded in [Cubiomes Viewer](https://github.com/Cubitect/cubiomes-viewer).

Here are a couple of examples, comparing the new sampled colormap to [Chunkbases's](https://www.chunkbase.com), which is based on AMIDST.

![Minecraft 1.17, Seed 2819277292818](mc17_2819277292818.png
"Minecraft 1.17, Seed 2819277292818, Chunkbase (left) vs Sampled (right)")
^ Minecraft 1.17, Seed 2819277292818, Chunkbase (left) vs Sampled (right)


![Minecraft 1.21, Seed 1642716](mc21_1642716.png
"Minecraft 1.21, Seed 1642716, Chunkbase (left) vs Sampled (right)")
^ Minecraft 1.21, Seed 1642716, Chunkbase (left) vs Sampled (right)


## Generation Process

The selection of sampled blocks and their contributions is specified in [biome_blocks.txt](biome_blocks.txt)
and was inspired by the [Minecraft Wiki](https://minecraft.wiki/w/Biome) page for each biome.
The contribution factor for each block is loosely based on the abundance of the blocks in that biome.
However, the values are a degree of freedom that I've often adjusted to achive certain results.

The biome color is then determined by a weighted average of the sample colors
(their mean value in the [Oklab](https://bottosson.github.io/posts/oklab/) colorspace).
Some of the biome variants have a block palette that is too similar to the main biome to use this process,
and instead apply a small offset in lightness to the main biome color.

After the average colors are determined, the contrast between some of the biomes may be a little low.
To improve open this, one can apply optimization passes, which nudge the biome colors so that they become more distinct.
This movement is constrained to the interpolated colorspace of the sample colors.


## Running the Script

To generate the colors yourself, you first need to extract the block assests folder from a Minecraft Java Client.
These are located at `/assets/minecraft/textures/block` inside the Minecraft Jar-File (1.21.3).

You can then run the `biome_samples.py` script, specifying the directory of the block assets as the first argument and the number of color-optimization passes you want to apply as the second argument.

E.g.:
```
biomes_samples.py ./block/ 20
```

