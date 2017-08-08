import os
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path

from git import Repo

from gitsubrepo.exceptions import NotAGitRepositoryException, NotAGitReferenceException, UnstagedChangeException, \
    NotAGitSubrepoException
from gitsubrepo.subrepo import clone, status, pull
from gitsubrepo.tests._resources.information import TEST_TAG, TEST_TAG_COMMIT, TEST_TAG_FILE, TEST_BRANCH, \
    TEST_BRANCH_COMMIT, \
    TEST_BRANCH_FILE, TEST_COMMIT, TEST_COMMIT_BRANCH, TEST_COMMIT_FILE, TEST_COMMIT_2, TEST_COMMIT_2_BRANCH, \
    TEST_COMMIT_2_FILE, TEST_REPOSITORY_ARCHIVE, TEST_REPOSITORY_NAME

TEST_DIRECTORY_NAME = "test-directory"
TEST_GIT_REPO_DIRECTORY_NAME = "git-directory"
TEST_NAME = "test-name"
TEST_EMAIL = "test@test-email"


class _TestWithSubrepo(unittest.TestCase):
    """
    Base class for tests involving sub-repos.
    """
    def setUp(self):
        self.temp_directory = tempfile.mkdtemp()

        with tarfile.open(TEST_REPOSITORY_ARCHIVE) as archive:
            archive.extractall(path=self.temp_directory)
        self.external_git_repository = os.path.join(self.temp_directory, TEST_REPOSITORY_NAME)

        self.git_directory = os.path.join(self.temp_directory, TEST_GIT_REPO_DIRECTORY_NAME)
        self.git_repository_client = Repo.init(self.git_directory)

        self.subrepo_directory = os.path.join(self.git_directory, TEST_DIRECTORY_NAME)

    def tearDown(self):
        shutil.rmtree(self.temp_directory)


class TestClone(_TestWithSubrepo):
    """
    Tests for `clone`.
    """
    def test_clone_inside_non_git_directory(self):
        self.assertRaises(NotAGitRepositoryException, clone, self.temp_directory,
                          os.path.join(self.temp_directory, TEST_DIRECTORY_NAME), tag=TEST_TAG)

    def test_clone_outside_directory(self):
        self.assertRaises(NotAGitRepositoryException, clone, self.git_directory,
                          os.path.join(self.temp_directory, TEST_DIRECTORY_NAME), tag=TEST_TAG)

    def test_clone_to_relative_directory(self):
        self.assertRaises(ValueError, clone, self.external_git_repository, TEST_DIRECTORY_NAME)

    def test_clone_to_existing_directory(self):
        test_directory = os.path.join(self.temp_directory, TEST_DIRECTORY_NAME)
        os.makedirs(test_directory)
        self.assertRaises(ValueError, clone, self.external_git_repository, test_directory, tag=TEST_TAG)

    def test_clone(self):
        commit = clone(self.external_git_repository, self.subrepo_directory)
        self.assertEqual(TEST_COMMIT_2[0: 7], commit)

    def test_clone_to_into_non_existent_path(self):
        deep = os.path.join(self.subrepo_directory, "deep")
        os.makedirs(deep)
        commit = clone(self.external_git_repository, os.path.join(deep, "deeper"))
        self.assertEqual(TEST_COMMIT_2[0: 7], commit)

    def test_clone_tag(self):
        commit = clone(self.external_git_repository, self.subrepo_directory, tag=TEST_TAG)
        self.assertEqual(TEST_TAG_COMMIT, commit)
        self.assertTrue(os.path.exists(os.path.join(self.subrepo_directory, TEST_TAG_FILE)))

    def test_clone_branch(self):
        commit = clone(self.external_git_repository, self.subrepo_directory, branch=TEST_BRANCH)
        self.assertEqual(TEST_BRANCH_COMMIT, commit)
        self.assertTrue(os.path.exists(os.path.join(self.subrepo_directory, TEST_BRANCH_FILE)))

    def test_clone_commit_on_master(self):
        commit = clone(
            self.external_git_repository, self.subrepo_directory, commit=TEST_COMMIT_2, branch=TEST_COMMIT_2_BRANCH)
        self.assertEqual(TEST_COMMIT_2[0:7], commit)
        self.assertTrue(os.path.exists(os.path.join(self.subrepo_directory, TEST_COMMIT_2_FILE)))

    def test_clone_commit_not_on_master(self):
        commit = clone(
            self.external_git_repository, self.subrepo_directory, commit=TEST_COMMIT, branch=TEST_COMMIT_BRANCH)
        self.assertEqual(TEST_COMMIT[0:7], commit)
        self.assertTrue(os.path.exists(os.path.join(self.subrepo_directory, TEST_COMMIT_FILE)))

    def test_clone_invalid_url(self):
        self.assertRaises(NotAGitRepositoryException, clone, "http://www.example.com/", self.subrepo_directory)

    def test_clone_invalid_branch(self):
        self.assertRaises(NotAGitReferenceException,
                          clone, self.external_git_repository, self.subrepo_directory, branch="non-existent")

    def test_clone_with_both_branch_and_tag(self):
        self.assertRaises(ValueError, clone,
                          "http://www.example.com/", self.subrepo_directory, branch=TEST_BRANCH, tag=TEST_TAG)

    def test_clone_when_uncommited_changes(self):
        Path(os.path.join(self.git_directory, "example-file")).touch()
        self.git_repository_client.git.add("--all")
        self.assertRaises(UnstagedChangeException, clone, self.external_git_repository, self.subrepo_directory)

    def test_clone_with_specific_author(self):
        clone(self.external_git_repository, self.subrepo_directory, author_name=TEST_NAME, author_email=TEST_EMAIL)
        latest_commit = self.git_repository_client.commit()
        self.assertEqual(TEST_NAME, latest_commit.author.name)
        self.assertEqual(TEST_EMAIL, latest_commit.author.email)

        clone(self.external_git_repository, os.path.join(self.git_directory, "other"))
        latest_commit = self.git_repository_client.commit()
        self.assertNotEqual(TEST_NAME, latest_commit.author.name)
        self.assertNotEqual(TEST_EMAIL, latest_commit.author.email)


class TestStatus(_TestWithSubrepo):
    """
    Tests for `status`.
    """
    def test_status_of_non_existent_directory(self):
        self.assertRaises(ValueError, status, os.path.join(self.git_directory, TEST_DIRECTORY_NAME))

    def test_status_in_non_git_repository(self):
        self.assertRaises(NotAGitRepositoryException, status, self.temp_directory)

    def test_status_of_git_directory(self):
        self.assertRaises(NotAGitSubrepoException, status, self.git_directory)

    def test_status_of_git_directory_when_subrepos_exist(self):
        clone(self.external_git_repository, self.subrepo_directory)
        self.assertRaises(NotAGitSubrepoException, status, self.git_directory)

    def test_status(self):
        clone(self.external_git_repository, self.subrepo_directory,branch=TEST_BRANCH)
        url, branch, commit = status(self.subrepo_directory)
        self.assertEqual(url, self.external_git_repository)
        self.assertEqual(branch, TEST_BRANCH)
        self.assertEqual(commit, TEST_BRANCH_COMMIT)


class TestPull(_TestWithSubrepo):
    """
    Tests for `pull`.
    """
    def test_pull_of_non_existent_directory(self):
        self.assertRaises(ValueError, pull, os.path.join(self.git_directory, TEST_DIRECTORY_NAME))

    def test_pull_when_uncommited_changes(self):
        clone(self.external_git_repository, self.subrepo_directory, branch=TEST_BRANCH)
        Path(os.path.join(self.git_directory, "example-file")).touch()
        self.git_repository_client.git.add("--all")
        self.assertRaises(UnstagedChangeException, pull, self.subrepo_directory)

    def test_pull_when_up_to_date(self):
        clone(self.external_git_repository, self.subrepo_directory, branch=TEST_BRANCH)
        self.assertEqual(TEST_BRANCH_COMMIT, pull(self.subrepo_directory))

    def test_pull_when_not_up_to_date(self):
        mutable_remote = os.path.join(self.temp_directory, "mutable-remote")
        Repo(self.external_git_repository).clone(mutable_remote)

        clone(mutable_remote, self.subrepo_directory, branch=self.git_repository_client.active_branch.name)

        Path(os.path.join(mutable_remote, "example-file")).touch()
        index = Repo(mutable_remote).index
        index.add(["example-file"])
        new_commit = index.commit("New commit").hexsha

        self.assertEqual(new_commit[0:7], pull(self.subrepo_directory))


if __name__ == "__main__":
    unittest.main()
