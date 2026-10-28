# Inputs for the larger planar search

Use the explicit graph encodings in [Grasegger, appendix A](https://arxiv.org/html/2502.04736v1#A1) and record the exact source version and encoding order. The validator deliberately accepts explicit edges, so an encoding-order error cannot be hidden inside the checker. Independent decoding of the appendix is still needed.

Passing the sparsity inequalities validates a graph prerequisite. It does not exhibit lengths, count realizations or certify a lower bound. Each future search must pin its graph, rational lengths, seed, budget, candidate boxes and independent-check logs.
