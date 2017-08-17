import os
import math


def shuffle(width=4096, height=4096):
    """
    For either selected read nodes in the compositing script, shuffle out all channels contained and create a write node for each channel.
    """
    exr_data = {
        'channels': 'rgb',
        'file_type': 'exr',
        'datatype': '16 bit half',
        'compression': 'Zip (1 scanline)',
        'reading': True
    }
    import nuke
    for read in nuke.selectedNodes():
        if read.Class() != 'Read':
            continue
        shuffle_nodes = []
        for layer in nuke.layers(read):
            shuffle = nuke.nodes.Shuffle(name='shuffle_{0}'.format(layer),
                                         inputs=[read])
            shuffle['in'].setValue(layer)
            shuffle['alpha'].setValue('black')
            shuffle_nodes.append(shuffle)
            write = nuke.nodes.Write(name='write_{0}'.format(layer),
                                     inputs=[shuffle])
            write['file'].setValue('{0}.{1}.exr'.format(
                read['file'].value().replace('.exr', ''),
                layer))
            write['file_type'].setValue(exr_data['file_type'])
            for attr, value in exr_data.iteritems():
                write[attr].setValue(value)
        contact = nuke.nodes.ContactSheet(inputs=shuffle_nodes)
        contact['width'].setValue(width)
        contact['height'].setValue(height)
        sqrt = math.ceil(math.sqrt(len(shuffle_nodes)))
        contact['rows'].setValue(sqrt)
        contact['columns'].setValue(sqrt)
        contact_write = nuke.nodes.Write(name='write_{0}_contact_sheet'.format(
            layer),
            inputs=[contact])
        contact_write['file'].setValue('{0}.ContactSheet.exr'.format(
            read['file'].value().replace('.exr', '')))
        for attr, value in exr_data.iteritems():
            contact_write[attr].setValue(value)


def create():
    """
    For a selected group of read nodes from the same rendering process (i.e.
    same naming pattern, using "." as a separator for Render Elements), create
    a multichannel EXR.
    """
    def is_number(value):
        """
        Check if a value is a number by trying to cast it as an integer

        :param value: Input value to check
        :type: any
        """
        try:
            int(value)
            return True
        except ValueError:
            return False

    exr_data = {
        'channels': 'all',
        'file_type': 'exr',
        'datatype': '16 bit half',
        'compression': 'Zip (1 scanline)',
        'reading': True
    }
    copy_data = {
        'from0': 'red',
        'to0': '{0}.red',
        'from1': 'green',
        'to1': '{0}.green',
        'from2': 'blue',
        'to2': '{0}.blue',
        'from3': 'none',
        'to3': 'none'
    }
    import nuke
    if not nuke.selectedNodes():
        return
    passes = []
    rgba = None
    for node in nuke.selectedNodes():
        if node.Class() != 'Read':
            continue
        fp_base = os.path.basename(node['file'].value())
        split_vals = fp_base.split('.')
        if len(split_vals) > 2 and not is_number(split_vals[-2]):
            passes.append(node)
        else:
            rgba = node
    last_copy = None
    for pass_read in sorted(passes, key=lambda x:
        os.path.basename(x['file'].value()).split('.')[-2].lower()):
        pass_name = os.path.basename(pass_read['file'].value()).split('.')[-2]
        nuke.Layer(pass_name, ['{0}.red'.format(pass_name),
                               '{0}.green'.format(pass_name),
                               '{0}.blue'.format(pass_name)])
        if not last_copy:
            copy = nuke.nodes.Copy(name='copy_{0}'.format(pass_name),
                                   inputs=[rgba, pass_read])
            last_copy = copy
        else:
            copy = nuke.nodes.Copy(name='copy_{0}'.format(pass_name),
                                   inputs=[last_copy, pass_read])
            last_copy = copy
        for attr, value in copy_data.iteritems():
            copy[attr].setValue(value.format(pass_name))
    write = nuke.nodes.Write(name='multichannel_write', inputs=[last_copy])
    write['file'].setValue(rgba['file'].value().replace('.exr',
                                                        '_multichannel.exr'))
    for attr, value in exr_data.iteritems():
            write[attr].setValue(value)
