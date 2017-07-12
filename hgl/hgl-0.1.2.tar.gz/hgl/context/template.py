#!/usr/bin/python
import os
import gc
import ctypes
import OpenGL
from OpenGL.GL import shaders
from OpenGL import GL
from PIL import Image
import numpy as np

# PYOPENGL_PLATFORM="osmesa"


class template_context(object):
    # camera properties
    viewport = 0, 0, 400, 400  # size of your screen / window drawing area
    viewport_centre = 200, 200  # size of your screen / window drawing area
    viewport_aspect = viewport[2] / viewport[3]
    field_of_view = 45
    lookat = (0.0, 0.0, 0.0)
    location = (0.0, 0.0, 80.0)
    near_plane = 10
    far_plane = 100.0

    # test triangle
    vertex_size = 3
    vertex_list = np.array([
         0.6,  0.6, 0.0,
        -0.6,  0.6, 0.0,
         0.0, -0.6, 0.0],
        dtype=np.float32)
    vertex_size = 3
    vertex_stride = vertex_size * 4

    texture_id = None
    texture_offset = 0

    default_vertex_shader = ["""
        #version 330
        in vec3 vertex_pos;
        void main()
        {
            gl_Position = vec4(vertex_pos, 1.0);
        }"""]

    default_fragment_shader = ["""
        #version 330
        out vec4 fragColor;
        void main()
        {
            fragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }"""]
    shader = None

    def __init__(self, version=(4, 5)):
        raise NotImplementedError

    def __call__(self, version=(4, 5)):
        self.__init__(version)


    def widget_error(self, widget):
        pass

    def info(self):
        print("Using %s display manager" % os.getenv('XDG_SESSION_TYPE'))
        print("PYOPENGL_PLATFORM env = %s " % os.getenv('PYOPENGL_PLATFORM', 'Not set'))

        for plugin in OpenGL.PlatformPlugin.all():
            if plugin.loaded:
                print('PYOPENGL Using %s ' % plugin.name)

    def test_opengl_methods(self):
        if bool(GL.glGenVertexArrays) is False:
            print('glGenVertexArrays not available on this machine')

    def update(self):
        self.test_opengl_methods()
        vs = shaders.compileShader(
            self.default_vertex_shader,
            GL.GL_VERTEX_SHADER)
        fs = shaders.compileShader(
            self.default_fragment_shader,
            GL.GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vs, fs)

        # Create a new Vertex Array Object
        self.vertex_array_object = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vertex_array_object)

        # Generate a new array buffers for our vertices
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)

        # Get position variable form the shader and store
        self.position = GL.glGetAttribLocation(self.shader, 'vertex_pos')
        GL.glEnableVertexAttribArray(self.position)

        # describe the data layout
        # GL.glVertexAttribPointer(
        #     self.position, 4, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))


            # glUniformMatrix4fv(shader.simple_matrix_model_view, 1, GL_FALSE, matrix_model_view)
            # glUniformMatrix4fv(shader.simple_matrix_projection, 1, GL_FALSE, matrix_projection)
# // connect the uv coords to the "vertTexCoord" attribute of the vertex shader
# glEnableVertexAttribArray(gProgram->attrib("vertTexCoord"));
# glVertexAttribPointer(gProgram->attrib("vertTexCoord"), 2, GL_FLOAT, GL_TRUE,  5*sizeof(GLfloat), (const GLvoid*)(3 * sizeof(GLfloat)));


        GL.glVertexAttribPointer(
            index=self.position,
            size=3,
            type=GL.GL_FLOAT,
            normalized=GL.GL_FALSE,
            stride=self.vertex_stride,
            pointer=ctypes.c_void_p(0))

        # because this is just for quick demos and will likely be overriden
        # give easy way of enabling a texture
        if self.texture_id is not None:
            self.tex_uniform = GL.glGetUniformLocation( self.shader, 'quad_texture')
            self.tex_coord = GL.glGetAttribLocation(self.shader, 'texture_pos')
            GL.glEnableVertexAttribArray(self.tex_coord)
            GL.glVertexAttribPointer(
                index=self.tex_coord,
                size=2,
                type=GL.GL_FLOAT,
                normalized=GL.GL_FALSE,
                stride=self.vertex_stride,
                pointer=ctypes.c_void_p(3*4))

        # data size, vertex length
        buffer_size = 4 * len(self.vertex_list)
        # Copy data to the buffer
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            buffer_size,
            self.vertex_list,
            GL.GL_STATIC_DRAW)

        # Unbind buffers once done
        GL.glBindVertexArray(0)
        if self.texture_id is not None:
            GL.glDisableVertexAttribArray(self.tex_coord)
        GL.glDisableVertexAttribArray(self.position)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def draw_data(self):
        if self.texture_id:
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
            GL.glUniform1i(self.tex_uniform, 0)
        GL.glBindVertexArray(self.vertex_array_object)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
        GL.glBindVertexArray(0)

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glUseProgram(self.shader)

        self.draw_data()

        GL.glUseProgram(0)
        GL.glFlush()

    def render(self):
        self.draw()

    def save(self, filename='/tmp/pyopengl_context.png'):
        """Draw the context and read the pixels one by one,
        pass to pil as image an save"""
        self.draw()

        buffer = (GL.GLubyte * (4 * self.viewport[2] * self.viewport[3]))(0)

        GL.glReadPixels(
            0,
            0,
            self.viewport[2],
            self.viewport[3],
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            buffer)

        # Use PIL to convert raw RGB buffer and flip the right way up
        image = Image.frombytes(
            mode="RGBA",
            size=(self.viewport[2], self.viewport[3]),
            data=buffer)

        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        image.save(filename)
        image.close()
        buffer = None
        self.quit()
        return filename

    def quit(self):
        gc.collect()

    def run(self):
        raise NotImplementedError

    def test(self):
        raise NotImplementedError
