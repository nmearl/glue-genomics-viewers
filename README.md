# glue-genomics-viewers
Glue viewers for genomics data

## Genome Track Viewer

Enables and the display and interaction of genome data, including semi-continuous functions on the genome (e.g. coverage files) and loop data showing connection between different parts of the genome. Multiple datasets can be visualized as separate axes on the viewer by drag-and-dropping, and subsets are visualized on these datasets. Dataset display order can be set by dragging and dropping the Plot Layers around. 

Smooth panning/zooming performance is enabled by first tiling the data (generating multiple downsampled versions of the full dataset), which is unoptimized and slow, but only needs to be done once for a dataset. The glue Data object for these datasets (`GenomicData`) is mostly just a reference to the tiled data on disk, not a full normal glue dataset, and does not currently work in other glue Data Viewers.

![MotifViewer](https://user-images.githubusercontent.com/3639698/134025407-ae5ac8fc-63c3-4fe8-994c-84e0a6a720d6.png)

## Heatmap Viewer

A modified version of the core Image Viewer, this enables the display of matrix-type data, aka heatmaps. This viewer does not generate a heatmap from counts of categorical variables, it assumes such a dataset already exists. Metadata about the rows and columns of the metadata is enabled by using `join_on_key` and selecting the associated joined dataset in the UI options. The built-in clustering Toolbar item allows for hierarchical clustering of the heatmap, and can display the dendrogram used for clustering to enable further subset selection and analysis.

![Dendogram](https://user-images.githubusercontent.com/3639698/134026573-a02135a5-30c5-445e-9056-5212986c397e.png)

## Network Viewer

Currently part of https://github.com/gluesolutions/glue-genomics-data, this viewer uses networkX to provide visualization of correlations and other connections between different entities (including regions on the genome).
