import torch as th


class MaxNormDefaultConstraint(object):
    """
    Applies max L2 norm 2 to the weights until the final layer and L2 norm 0.5
    to the weights of the final layer as done in [1]_.
    
    References
    ----------

    .. [1] Schirrmeister, R. T., Springenberg, J. T., Fiederer, L. D. J., 
       Glasstetter, M., Eggensperger, K., Tangermann, M., ... & Ball, T. (2017).
       Deep learning with convolutional neural networks for brain mapping and
       decoding of movement-related information from the human EEG.
       arXiv preprint arXiv:1703.05051.
    
    """
    def apply(self, model):
        last_weight = None
        for name, module in list(model.named_children()):
            if hasattr(module, 'weight') and (
                    not module.__class__.__name__.startswith('BatchNorm')):
                module.weight.data = th.renorm(module.weight.data,2,0,maxnorm=2)
                last_weight = module.weight
        if last_weight is not None:
            last_weight.data = th.renorm(last_weight.data,2,0,maxnorm=0.5)