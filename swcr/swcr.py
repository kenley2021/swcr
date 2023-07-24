# -*- coding: utf-8 -*-
import logging
import pkg_resources
from os.path import abspath
from os import scandir
from pathlib import Path

import click
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

logger = logging.getLogger(__name__)

DEFAULT_INDIRS = ['.']
DEFAULT_EXTS = ['c', 'h']
DEFAULT_COMMENT_CHARS = ['/*', '*', '*/', '//']

def del_slash(dirs):
    return [dir_[:-1] if dir_[-1] == '/' else dir_ for dir_ in dirs]

class CodeFinder(object):
    def __init__(self, exts=None):
        self.exts = exts if exts else DEFAULT_EXTS

    def is_code(self, file):
        return any(file.endswith(ext) for ext in self.exts)

    @staticmethod
    def is_hidden_file(file):
        return file[0] == '.'

    @staticmethod
    def should_be_excluded(file, excludes=None):
        if not excludes:
            return False
        if not isinstance(excludes, list):
            excludes = [excludes]
        return any(file.startswith(exclude) for exclude in excludes)

    def find(self, indir, excludes=None):
        files = []
        for entry in scandir(indir):
            entry_name = entry.name
            entry_path = abspath(entry.path)
            if self.is_hidden_file(entry_name) or self.should_be_excluded(entry_path, excludes):
                continue
            if entry.is_file():
                if self.is_code(entry_name):
                    files.append(entry_path)
            else:
                files.extend(self.find(entry_path, excludes=excludes))
        logger.debug('%s directory:%d code files.', indir, len(files))
        return files

class CodeWriter(object):
    def __init__(self, font_name='宋体', font_size=10.5, space_before=0.0, space_after=2.3, line_spacing=10.5, command_chars=None, document=None):
        self.font_name = font_name
        self.font_size = font_size
        self.space_before = space_before
        self.space_after = space_after
        self.line_spacing = line_spacing
        self.command_chars = command_chars if not command_chars else DEFAULT_COMMENT_CHARS
        self.document = Document(pkg_resources.resource_filename('swcr', 'template.docx')) if not document else document

    @staticmethod
    def is_blank_line(line):
        return not bool(line.strip())

    def is_comment_line(self, line):
        return any(line.lstrip().startswith(comment_char) for comment_char in self.command_chars)

    def write_header(self, title):
        paragraph = self.document.sections[0].header.paragraphs[0]
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = paragraph.add_run(title)
        run.font.name = self.font_name
        run.font.size = Pt(self.font_size)
        return self

    def check_file_encoding(self, file_path):
        """ check file encoding """
        import chardet
        with open(file_path, 'rb') as fd:
            encode_str = chardet.detect(fd.read())['encoding']
            logging.info("input_file: {0}, encoding: {1}".format(file_path, encode_str))
            return encode_str

    def write_file(self, file):
        with open(file, encoding=self.check_file_encoding(file)) as fp:
            for line in fp:
                line = line.rstrip()
                blank_line = self.is_blank_line(line)
                comment_line = self.is_comment_line(line)
                if blank_line or comment_line:
                    continue
                paragraph = self.document.add_paragraph()
                paragraph.paragraph_format.space_before = Pt(self.space_before)
                paragraph.paragraph_format.space_after = Pt(self.space_after)
                paragraph.paragraph_format.line_spacing = Pt(self.line_spacing)
                run = paragraph.add_run(line)
                run.font.name = self.font_name
                run.font.size = Pt(self.font_size)
        return self

    def save(self, file):
        self.document.save(file)

@click.command(name='swcr')
@click.option(
    '-t', '--title', default='软件著作权程序鉴别材料生成器V1.0',
    help='软件名称+版本号，默认为软件著作权程序鉴别材料生成器V1.0，此名称用于生成页眉'
)
@click.option(
    '-i', '--indir', 'indirs',
    multiple=True, type=click.Path(exists=True),
    help='源码所在文件夹，可以指定多个，默认为当前目录'
)
@click.option(
    '-e', '--ext', 'exts',
    multiple=True, help='源代码后缀，可以指定多个，默认为Python源代码'
)
@click.option(
    '-c', '--comment-char', 'comment_chars',
    multiple=True, help='注释字符串，可以指定多个，默认为#、//'
)
@click.option(
    '--font-name', default='宋体',
    help='字体，默认为宋体'
)
@click.option(
    '--font-size', default=10.5,
    type=click.FloatRange(min=1.0),
    help='字号，默认为五号，即10.5号'
)
@click.option(
    '--space-before', default=0.0,
    type=click.FloatRange(min=0.0),
    help='段前间距，默认为0'
)
@click.option(
    '--space-after', default=2.3,
    type=click.FloatRange(min=0.0),
    help='段后间距，默认为2.3'
)
@click.option(
    '--line-spacing', default=10.5,
    type=click.FloatRange(min=0.0),
    help='行距，默认为固定值10.5'
)
@click.option(
    '--exclude', 'excludes',
    multiple=True, type=click.Path(exists=True),
    help='需要排除的文件或路径，可以指定多个'
)
@click.option(
    '-o', '--outfile', default='code.docx',
    type=click.Path(exists=False),
    help='输出文件（docx格式），默认为当前目录的code.docx'
)
@click.option('-v', '--verbose', is_flag=True, help='打印调试信息')
def main(
        title, indirs, exts,
        comment_chars, font_name,
        font_size, space_before,
        space_after, line_spacing,
        excludes, outfile, verbose
):
    if not indirs:
        indirs = DEFAULT_INDIRS
    if not exts:
        exts = DEFAULT_EXTS
    if not comment_chars:
        comment_chars = DEFAULT_COMMENT_CHARS
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    # 第零步，把所有的路径都转换为绝对路径
    indirs = [abspath(indir) for indir in indirs]
    excludes = del_slash(
        [abspath(exclude) for exclude in excludes] if excludes else []
    )

    # 第一步，查找代码文件
    finder = CodeFinder(exts)
    files = [file for indir in indirs for file in finder.find(
        indir, excludes=excludes
    )]

    # 第二步，逐个把代码文件写入到docx中
    writer = CodeWriter(
        command_chars=comment_chars,
        font_name=font_name,
        font_size=font_size,
        space_before=space_before,
        space_after=space_after,
        line_spacing=line_spacing
    )
    writer.write_header(title)
    for file in files:
        writer.write_file(file)
    writer.save(outfile)
    return 0

if __name__ == '__main__':
    main()