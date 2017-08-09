# -*- coding: utf-8 -*-
import abc
from watson.db.contextmanagers import transaction_scope

class Criteria(metaclass=abc.ABCMeta):
    """The base criteria class.
    """
    @abc.abstractmethod
    def apply(self, query):
        """Called by the repository on all criteria.

        Args:
            query: The SqlAlchemy query to be used

        Returns:
            An adjusted SqlAlchemy query
        """
        raise NotImplementedError('You must implement apply for this criteria')


class Base(metaclass=abc.ABCMeta):
    """Provides common interactions with the SQLAlchemy session.

    Example:

    .. code-block:: python

        class MyRepository(Base):
            __model__ = models.MyModel

        # sqlalchemy_session is a reference to a Session object
        repo = MyRepository(sqlalchemy_session)
        mymodel = repo.new(attr='Value')
        print(mymodel.attr)  # 'Value'
        repo.save(mymodel)

    Attributes:
        session (Session): The SqlAlchemy session
        __model__ (mixed): The model object the server interacts with
    """
    session = None
    __model__ = None

    def __init__(self, session):
        """
        Args:
            session (Session): The SqlAlchemy session
        """
        self.session = session

    @property
    def query(self):
        return self.session.query(self.__model__)

    def all(self):
        """
        Returns:
            list: A list of all model objects
        """
        return self.query.all()

    def get(self, id, error_on_not_found=False):
        """Retrieve a single object based on it's ID.

        Args:
            id (int): The primary key of the record
            error_on_not_found (bool): Raise an exception if not found

        Returns:
            mixed: The matching model object

        Raises:
            Exception when no matching results are found.
        """
        obj = self.query.get(id)
        if not obj and error_on_not_found:
            raise Exception('No matching result found.')
        return obj

    # Convenience methods

    def find_by_criteria(self, *criterias):
        """Find all models by a list of criterias.

        Applies a list of criteria to the query.

        Args:
            criterias: A list of watson.db.repositories.Criteria objects

        Returns:
            The query to be iterated over
        """
        query = self.query
        for criteria in criterias:
            query = criteria.apply(query)
        return query

    def get_by_criteria(self, *criterias, raise_error=True):
        """Find an individual model based on a list of criterias.

        Args:
            criterias: A list of watson.db.repositories.Criteria objects
            raise_error: Whether or not a NotFoundError should be raised if
                         the model cannot be found

        Returns:
            The query to be iterated over
        """
        result = self.find_by_criteria(*criterias).first()
        if not result and raise_error:
            raise Exception('No matching result found.')
        return result

    def find(self, **kwargs):
        """Shorthand for the filter_by method.

        Should be used when performing query specific operations (such as
        bulk deletion)

        Args:
            kwargs: The fields to search for
        """
        return self.query.filter_by(**kwargs)

    def first(self, **kwargs):
        """Return the first matching result for the query.

        Args:
            kwargs: The fields to search for

        Returns:
            mixed: The object found, or None if nothing was returned
        """
        return self.find(**kwargs).first()

    def delete(self, model):
        """Deletes a model from the database.

        Args:
            model (mixed): The model to delete
        """
        with transaction_scope(self.session) as session:
            session.delete(model)

    def delete_all(self, *models):
        """Delete a list of models.

        If deleting more than a single model of the same type, then
        a Repository.find(**kwargs).delete() should be called (and wrapped in a
        transaction_scope) instead.

        Args:
            models (list): The models to delete
        """
        with transaction_scope(self.session) as session:
            for model in models:
                session.delete(model)

    def new(self, **kwargs):
        """Creates a new instance of the model object

        Args:
            kwargs (mixed): The initial values for the model

        Returns:
            mixed: The newly created model
        """
        return self.__model__(**kwargs)

    def save(self, model):
        """Add the model to the session and save it to the database.

        Args:
            model (mixed): The object to save

        Returns:
            mixed: The saved model
        """
        with transaction_scope(self.session) as session:
            session.add(model)
        return model

    def save_all(self, *models):
        """Save a list of models.

        Args:
            models (list, tuple): The models to save
        """
        with transaction_scope(self.session) as session:
            for model in models:
                session.add(model)
        return True

    def count(self):
        """Returns the total number of model objects

        Return:
            int
        """
        return self.query.count()

    def update(self, **kwargs):
        raise NotImplementedError()
