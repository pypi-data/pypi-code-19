"""
Generic upload asset chain.

NOTE: The generic upload chain is designed to handle a single file upload,
multiple file uploads client side should result in multiple calls to the upload
chain.
"""

import flask
from manhattan.assets.transforms.images import Fit, Output
from manhattan.assets.backends import exceptions
from manhattan.chains import Chain, ChainMgr

from manhattan.manage.views import factories
from manhattan.manage.views import utils

__all__ = ['upload_chains']


# Define the chains
upload_chains = ChainMgr()

# POST
upload_chains['post'] = Chain([
    'authenticate',
    'store_asset',
    [
        ['success'],
        ['fail']
    ]
])


# Define the links
upload_chains.set_link(factories.authenticate())

@upload_chains.link
def store_asset(state):
    """
    Store the file uploaded as an asset.

    The client request is expected to include a file under the parameter name of
    `file`.

    If the file is successfully stored this links adds an `asset` key to the
    state containing the `Asset` instance representing the uploaded file.

    If the file could not be stored then this link adds a `error_msg` key to the
    state containing a description of why the file failed validation.

    IMPORTANT: Validation of the asset itself is the responsibility of the view
    that is storing the associated parent document, not the upload chain. The
    upload chain merely validates that a file was provided and could be stored.
    """

    # Check a file was provided
    if 'file' not in flask.request.files \
            or not flask.request.files['file'].filename:

        state.error_msg = 'No file sent'
        return False

    # Attempt to store the file
    file = flask.request.files['file']
    asset_mgr = flask.current_app.asset_mgr
    try:
        state.asset = asset_mgr.store_temporary((file.filename, file))
    except exceptions.StoreError as e:
        state.error_msg = str(e)
        return False

    # If the asset is an image then create a base variation
    if state.asset.type == 'image':

        # The `--base--` variation is used to allow the user to perform and
        # preview transforms against the image, a `Fit` transform is applied to
        # the image initially to restrict the size of the image and help with
        # performance.
        #
        # The `--thumb--` variation is used to provide a thumbnail view of the
        # image.
        try:
            config = flask.current_app.config
            base_size = config.get('ASSET_BASE_SIZE', [600, 600])
            thumb_size = config.get('ASSET_THUMB_SIZE', [300, 300])
            asset_mgr.generate_variations(
                state.asset,
                {
                    '--base--': [
                        Fit(base_size[0], base_size[1]),
                        Output('jpg', 75)
                        ],
                    '--thumb--': [
                        Fit(thumb_size[0], thumb_size[1]),
                        Output('jpg', 50)
                        ]
                }
            )
        except exceptions.StoreError as e:
            state.error_msg = str(e)
            return False

    return True

@upload_chains.link
def success(state):
    """
    Return a successful response with the uploaded `asset` included in the
    payload.
    """
    return utils.json_success({'asset': state.asset.to_json_type()})

@upload_chains.link
def fail(state):
    """Return a failed response with the `error_message`"""
    return utils.json_fail(state.error_msg)