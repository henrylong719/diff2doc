"""Tests for the git diff extraction stage."""
 
from subprocess import CompletedProcess
from unittest import result
from unittest.mock import MagicMock, patch
 
import pytest
 
from diff2doc.git_diff import get_diff


@patch("diff2doc.git_diff.subprocess.run")
def test_get_diff_returns_stdout_on_success(mock_run: MagicMock) -> None:
    """get_diff returns the raw stdout when git exits successfully."""
    
    mock_run.return_value = CompletedProcess(
		args=["git","diff","HEAD"],
		returncode=0,
		stdout="fake diff output\n",
		stderr=""
	)
    
    result = get_diff("HEAD")
    
    assert result == "fake diff output\n"
    mock_run.assert_called_once_with(
		["git", "diff", "HEAD"],
		capture_output=True,
		text=True
	)
    
@patch("diff2doc.git_diff.subprocess.run")
def test_get_dff_raises_on_git_failure(mock_run: MagicMock) -> None:
     """get_diff raises RuntimeError when git exits with a non-zero code."""
     mock_run.return_value = CompletedProcess(
		args=["git", "diff", "HEAD"],
		returncode=128,
		stdout="",
		stderr="fatal: not a git repository"
	 )
     
     with pytest.raises(RuntimeError, match="not a git repository"):
        get_diff("HEAD")
     
     
    
    
    
