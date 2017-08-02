from __future__ import unicode_literals
from glob import glob
import os
import io
from subprocess import call, Popen, PIPE
from fim import main
import pytest

@pytest.fixture
def stdin() :
    return io.StringIO('1\n2\n3')

@pytest.fixture
def big_stdin():
    s = ''.join(str(_)+'\n' for _ in range(30))
    return io.StringIO(s)
    
def test_cli_usage(stdin) :
    with pytest.raises(SystemExit) :
        main(['-h'],stdin=stdin)
    
def test_bad_substr(stdin) :
    with pytest.raises(SystemExit) :
        main(['-','-s','abc'],stdin=stdin)
        
def test_integration(tmpdir,stdin) :
    # create text files
    cmd = ['-','-e','seq 1 {} > {}.txt']
    main(cmd,stdin=stdin,cwd=str(tmpdir))
    assert len(tmpdir.listdir()) == 3
    
    norm_path = lambda p: os.path.basename(str(p))
    tmp_glob = lambda g: [norm_path(_) for _ in glob(os.path.join(str(tmpdir),g))]
    
    cmd = tmp_glob('*') + ['-e','mv {} number_{}']
    main(cmd,cwd=str(tmpdir))
    assert len(tmpdir.listdir()) == 3
    
    cmd = tmp_glob('*') + ['-e',r'cp {} {s:number_(\d).txt:number_\1by\1.txt:}']
    main(cmd,cwd=str(tmpdir))
    assert len(tmp_glob('*by*')) == 3
    
    cmd = tmp_glob('*by*') + ['-e','echo number | cat - {} > {s:.txt:_label.txt:}']
    print(cmd)
    print(tmp_glob('*by*'))
    main(cmd,cwd=str(tmpdir))
    assert len(tmp_glob('*label*')) == 3
    
    tmp_fn = [str(_) for _ in tmpdir.listdir() if '3_label' in str(_)]
    assert len(tmp_fn) == 1
    tmp_fn = tmp_fn[0]
    with open(tmp_fn) as f :
        lines = f.readlines()
        assert len(lines) == 4
        assert lines == ['number\n','1\n','2\n','3\n']
        
    cmd = tmp_glob('*_label.txt') + ['-e','ln -s {} symlink_to_{}']
    main(cmd,cwd=str(tmpdir))
    assert len(tmp_glob('*')) == 12 
    
    cmd = tmp_glob('*_label.txt') + ['-e','mv {} {c:basename %s .txt}.pdf']
    main(cmd,cwd=str(tmpdir))
    print(cmd)
    print(tmp_glob('*.pdf'))
    assert len(tmp_glob('*.pdf')) == 6
    assert len(tmp_glob('*_label.txt')) == 0
    
def test_procs(tmpdir,big_stdin) :
    # create text files
    cmd = ['-','-p','3','-e','seq 1 {} > {}.txt']
    main(cmd,stdin=big_stdin,cwd=str(tmpdir))
    assert len(tmpdir.listdir()) == 30
 