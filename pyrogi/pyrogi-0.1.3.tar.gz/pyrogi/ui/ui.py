from pyrogi.drawing import Drawable

class UIElementContainer(Drawable):
    """The :class:`UIElementContainer` class defines a :class:`Drawable` which
    can contain any number of :class:`UIElement` children. This class then
    passes events, such as ticks, draws, and mouse events, on to all of the
    children.

    The :code:`__init__` method of a :class:`UIElementContainer` is as follows:

    :param position: The position in tile space of the
        :class:`UIElementContainer`.
    :type position: Vec2
    """

    def __init__(self, position):
        super(UIElementContainer, self).__init__(position)
        self.ui_elements = []

    def on_tick(self, millis):
        """Called by this object's container when a tick occurs. This should
        never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every tick.
        The tick event is passed on to every child of this object, in addition
        to the object's own tick method.
        # TODO actually implement this last part.

        :param millis: The number of milliseconds since the last tick.
        :type millis: int
        """
        for elt in self.ui_elements[:]:
            elt.on_tick(millis)
            elt.update_drawable(millis)
    def on_draw(self, g):
        """Called by this object's container when a draw occurs. This should
        never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every draw.
        The draw event is passed on to every child of this object, in addition
        to the object's own draw method.

        :param g: The :class:`Graphics` object to be used to perform the
            drawing.
        :type g: Graphics
        """
        self.draw(g)
        for elt in self.ui_elements[:]:
            elt.on_draw(g)

    def add_child(self, child):
        """Add a new child to this object's child list.

        :param child: The child to add.
        :type child: UIElementContainer
        """
        self.ui_elements.append(child)
    def remove_child(self, child):
        """Remove the given child from this object's child list.

        :param child: The child to remove.
        :type child: UIElementContainer
        """
        self.ui_elements.remove(child)

    def handle_key_down(self, event):
        """Called by this object's container when a key down event occurs. This
        should never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every time
        the event is triggered.  The event is passed on to every child of this
        object, in addition to the object's own on_key_down method.

        :param event: The event triggered.
        :type event: KeyDownEvent
        """
        self.on_key_down(event)
        for elt in self.ui_elements[:]:
            elt.handle_key_down(event)
    def handle_key_up(self, event):
        """Called by this object's container when a key up event occurs. This
        should never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every time
        the event is triggered.  The event is passed on to every child of this
        object, in addition to the object's own on_key_up method.

        :param event: The event triggered.
        :type event: KeyUpEvent
        """
        self.on_key_up(event)
        for elt in self.ui_elements[:]:
            elt.handle_key_up(event)
    def handle_mouse_moved(self, event):
        """Called by this object's container when a mouse moved event occurs.
        This should never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every time
        the event is triggered.  The event is passed on to every child of this
        object, in addition to the object's own on_mouse_moved method.

        :param event: The event triggered.
        :type event: MouseMovedEvent
        """
        self.on_mouse_moved(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_moved(event)
    def handle_mouse_button_down(self, event):
        """Called by this object's container when a mouse button down event
        occurs.  This should never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every time
        the event is triggered.  The event is passed on to every child of this
        object, in addition to the object's own on_mouse_button_down method.

        :param event: The event triggered.
        :type event: MouseButtonDownEvent
        """
        self.on_mouse_button_down(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_button_down(event)
    def handle_mouse_button_up(self, event):
        """Called by this object's container when a mouse button up event
        occurs.  This should never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every time
        the event is triggered.  The event is passed on to every child of this
        object, in addition to the object's own on_mouse_button_up method.

        :param event: The event triggered.
        :type event: MouseButtonUpEvent
        """
        self.on_mouse_button_up(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_button_up(event)
    def handle_mouse_wheel_scrolled(self, event):
        """Called by this object's container when a mouse wheel scrolled event
        occurs.  This should never be overriden, but can be extended if the
        :class:`UIElementContainer` subclass wishes to do something every time
        the event is triggered.  The event is passed on to every child of this
        object, in addition to the object's own on_mouse_wheel_scrolled method.

        :param event: The event triggered.
        :type event: MouseWheelScrolledEvent
        """
        self.on_mouse_wheel_scrolled(event)
        for elt in self.ui_elements[:]:
            elt.handle_mouse_wheel_scrolled(event)

    def on_key_down(self, event):
        """A callback called by handle_key_down when a KeyDownEvent occurs.
        This method should be implemented by any subclass of
        :class:`UIElementContainer` which wants to act on this event.

        :param event: The event triggerd.
        :type event: KeyDownEvent
        """
        pass
    def on_key_up(self, event):
        """A callback called by handle_key_up when a KeyUpEvent occurs.
        This method should be implemented by any subclass of
        :class:`UIElementContainer` which wants to act on this event.

        :param event: The event triggerd.
        :type event: KeyUpEvent
        """
        pass
    def on_mouse_moved(self, event):
        """A callback called by handle_mouse_moved when a MouseMovedEvent
        occurs.  This method should be implemented by any subclass of
        :class:`UIElementContainer` which wants to act on this event.

        :param event: The event triggerd.
        :type event: MouseMovedEvent
        """
        pass
    def on_mouse_button_down(self, event):
        """A callback called by handle_mouse_button_down when a
        MouseButtonDownEvent occurs.  This method should be implemented by any
        subclass of :class:`UIElementContainer` which wants to act on this
        event.

        :param event: The event triggerd.
        :type event: MouseButtonDownEvent
        """
        pass
    def on_mouse_button_up(self, event):
        """A callback called by handle_mouse_button_up when a
        MouseButtonUpEvent occurs.  This method should be implemented by any
        subclass of :class:`UIElementContainer` which wants to act on this
        event.

        :param event: The event triggerd.
        :type event: MouseButtonUpEvent
        """
        pass
    def on_mouse_wheel_scrolled(self, event):
        """A callback called by handle_mouse_wheel_scrolled when a
        MouseWheelScrolledEvent occurs.  This method should be implemented by
        any subclass of :class:`UIElementContainer` which wants to act on this
        event.

        :param event: The event triggerd.
        :type event: MouseWheelScrolledEvent
        """
        pass

class UIElement(UIElementContainer):
    def __init__(self, screen, position, dimensions):
        UIElementContainer.__init__(self, position)
        self.screen = screen
        self.dimensions = dimensions
        self.mouse_down_on_element = False

    def on_tick(self, millis):
        pass

    def on_key_down(self, event):
        pass
    def on_key_up(self, event):
        pass
    def on_mouse_moved(self, event):
        if not self.contains_position(event.last_position) and self.contains_position(event.position):
            self.on_mouse_entered(event)
        elif self.contains_position(event.last_position) and not self.contains_position(event.position):
            self.on_mouse_left(event)
        elif self.contains_position(event.last_position) and self.contains_position(event.position):
            self.on_mouse_moved_inside(event)
    def on_mouse_button_down(self, event):
        if self.contains_position(event.position):
            self.mouse_down_on_element = True
            self.on_mouse_down(event)
    def on_mouse_button_up(self, event):
        if self.mouse_down_on_element and self.contains_position(event.position):
            self.on_clicked(event)
        self.mouse_down_on_element = False
        if self.contains_position(event.position):
            self.on_mouse_up(event)
    def on_mouse_wheel_scrolled(self, event):
        if self.contains_position(event.position):
            self.on_mouse_scrolled(event)

    def on_mouse_entered(self, event):
        pass
    def on_mouse_left(self, event):
        pass
    def on_mouse_moved_inside(self, event):
        pass
    def on_mouse_down(self, event):
        pass
    def on_mouse_up(self, event):
        pass
    def on_clicked(self, event):
        pass
    def on_mouse_scrolled(self, event):
        pass
