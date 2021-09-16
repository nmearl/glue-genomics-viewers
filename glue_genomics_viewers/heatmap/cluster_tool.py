from glue.config import viewer_tool
from glue.viewers.common.tool import Tool
import seaborn as sns
import pandas as pd
import scipy.cluster.hierarchy as hierarchy 

from glue.core.component import CategoricalComponent
from glue.core.component_id import ComponentID, PixelComponentID
from glue.core import Data
from glue.core.decorators import clear_cache
from glue.core.message import NumericalDataChangedMessage

from .heatmap_coords import HeatmapCoords
import numpy as np
import ete3


def getNewick(node, newick, parentdist, leaf_names):
    if node.is_leaf():
        return "%s:%.2f%s" % (leaf_names[node.id], parentdist - node.dist, newick)
    else:
        if len(newick) > 0:
            newick = "):%.2f%s" % (parentdist - node.dist, newick)
        else:
            newick = ");"
        newick = getNewick(node.get_left(), newick, node.dist, leaf_names)
        newick = getNewick(node.get_right(), ",%s" % (newick), node.dist, leaf_names)
        newick = "(%s" % (newick)
        return newick

def find_type(string):
    if string == '':
        return None

    if string.isnumeric():
        return int

    try:
        float(string)
        return float
    except ValueError:
        return str


def determine_format(fname):
    # formats described here
    # http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees

    # default to format=1, unless file has support values instead of internal
    # node names.

    t = ete3.Tree(fname, format=1)
    leaf_types = set(find_type(n.name) for n in t.traverse() if n.is_leaf())

    parent_types = set(find_type(n.name) for n in t.traverse() if not n.is_leaf())

    if len(leaf_types) != 1:
        # maybe revert to just str in this case?
        raise Exception('could not load tree, leaves are not homogenous types')

    if None in parent_types:
        parent_types.remove(None)

    if leaf_types != parent_types and parent_types == set([float]):
        # we have detected structure values, format 0 is correct
        return 0
    else:
        # no structures detected, use 1 (internal node names)
        return 1


def tree_process(newickstr, title):
    import ete3
    #result = Data(newickstr=[newickstr])
    result = Data()
    result.label = "%s [tree data]" % title
    tree = ete3.Tree(newickstr, format=determine_format(newickstr))
    result.tdata = tree
    result.tree_component_id = "tree nodes %s" % result.uuid

    # ignore nameless nodes as they cannot be indexed
    names = [n.name for n in tree.traverse("postorder") if n.name != ""]

    allint = all(name.isnumeric() for name in names)

    nodes = np.array([(int(name) if allint else name) for name in names])

    for node in tree.traverse("postorder"):
        if allint:
            node.idx = int(node.name) if node.name != "" else None
        else:
            node.idx = node.name

    result.add_component(CategoricalComponent(nodes), result.tree_component_id)

    return result


@viewer_tool
class ClusterTool(Tool):

    icon = 'glue_tree'
    tool_id = 'heatmap:cluster'
    action_text = 'Apply hierarchical clustering to matrix'
    tool_tip = 'Apply hierarchical clustering to matrix'
    shortcut = 'Ctrl+K'

    def __init__(self, viewer):
        super(ClusterTool, self).__init__(viewer)




    def activate(self):
        """
        We use seaborn.clustermap to cluster the data and then
        use the indices returned from this method to update the data components and
        update the Coords for the data object
        
        TODO: could/should also spawn a dendrogram showing connectedness
        """
        data = self.viewer.state.reference_data    
        
        g = sns.clustermap(data['counts']) #This should not be hard coded... I guess it should come from state
        new_row_ind = g.dendrogram_row.reordered_ind
        new_col_ind = g.dendrogram_col.reordered_ind
        
        orig_xticks = data.coords.x_axis_ticks
        orig_yticks = data.coords.y_axis_ticks
        orig_labels = data.coords._labels

        new_xticks = [orig_xticks[i] for i in new_col_ind]
        new_yticks = [orig_yticks[i] for i in new_row_ind]

        data.coords.x_axis_ticks = np.array(new_xticks)
        data.coords.y_axis_ticks = np.array(new_yticks)
        
        for component in data.components:
            if not isinstance(component, PixelComponentID):  # Ignore pixel components
                data.update_components({component:pd.DataFrame(data.get_data(component)).iloc[new_row_ind,new_col_ind]})
        
        print(g.dendrogram_col.linkage)
        yo = g.dendrogram_col.linkage
        yo[:,2] = yo[:,2]/np.max(yo[:,2]) #Normalize by max
        print(yo)
        tree = hierarchy.to_tree(yo, False)
        newicktree = getNewick(tree, "", tree.dist, orig_xticks)
        d2 = tree_process(newicktree,"experiment-tree")
        datacoll = self.viewer.session.data_collection
        datacoll.append(d2)
        
        data.join_on_key(d2, 'exp_ids', d2.tree_component_id)
        
        # We might need to update join_on_key mappings after we re-order things
        # for other_dataset, key_join in data._key_joins.items():
        #    print(f'other_dataset = {other_dataset}')
        #    print(f'key_join  = {key_join}')
        #    cid, cid_other = key_join
        #    data.join_on_key(other_dataset, cid, cid_other)
        
        #In theory this is already done in update_components
        #if data.hub is not None:
        #    msg = NumericalDataChangedMessage(data)
        #    data.hub.broadcast(msg)

        #if other_dataset.hub is not None:
        #    msg = NumericalDataChangedMessage(other_dataset)
        #    data.hub.broadcast(msg)

        #In theory this is already done in update_components
        #for subset in data.subsets:
        #    print(subset)
        #    clear_cache(subset.subset_state.to_mask)

        #for subset in other_dataset.subsets:
        #    clear_cache(subset.subset_state.to_mask)

        
        self.viewer._update_axes()

    def close(self):
        """
        If we wanted to make clustering not permanently change the dataset we could
        cache the original data and then restore it on close.
        """
        pass
