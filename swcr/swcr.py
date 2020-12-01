# -*- coding: utf-8 -*-
import logging
import pkg_resources
from os.path import abspath
try:
    from os import scandir
except ImportError:
    from scandir import scandir

import click
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


logger = logging.getLogger(__name__)


# 默认源代码文件目录
DEFAULT_INDIRS = ['.']
# 默认支持的代码格式
DEFAULT_EXTS = ['py']
# 默认的注释前缀
DEFAULT_COMMENT_CHARS = (
    '#', '//'
)


def del_slash(dirs):
    """
    删除文件夹最后一位的/

    Args:
        dirs: 文件夹列表
    Returns:
        删除之后的文件夹
    """
    no_slash_dirs = []
    for dir_ in dirs:
        if dir_[-1] == '/':
            no_slash_dirs.append(dir_[: -1])
        else:
            no_slash_dirs.append(dir_)
    return no_slash_dirs


class CodeFinder(object):
    """
    给定一个目录，和若干个后缀名，
    递归地遍历该目录，找到该目录下
    所有以这些后缀结束的文件
    """
    def __init__(self, exts=None):
        """
        Args:
            exts: 后缀名，默认为以py结尾
        """
        self.exts = exts if exts else ['py']

    def is_code(self, file):
        for ext in self.exts:
            if file.endswith(ext):
                return True
        return False

    @staticmethod
    def is_hidden_file(file):
        """
        是否是隐藏文件
        """
        return file[0] == '.'

    @staticmethod
    def should_be_excluded(file, excludes=None):
        """
        是否需要略过此文件
        """
        if not excludes:
            return False
        if not isinstance(excludes, list):
            excludes = [excludes]
        should_be_excluded = False
        for exclude in excludes:
            if file.startswith(exclude):
                should_be_excluded = True
                break
        return should_be_excluded

    def find(self, indir, excludes=None):
        """
        给定一个文件夹查找这个文件夹下所有的代码

        Args:
            indir: 需要查到代码的目录
            excludes: 排除文件或目录
        Returns:
            代码文件列表
        """
        files = []
        for entry in scandir(indir):
            # 防止根目录有一些含有非常多文件的隐藏文件夹
            # 例如，.git文件，如果不排除，此程序很难运行
            entry_name = entry.name
            entry_path = abspath(entry.path)
            if self.is_hidden_file(entry_name):
                continue
            if self.should_be_excluded(entry_path, excludes):
                continue
            if entry.is_file():
                if self.is_code(entry_name):
                    files.append(entry_path)
                continue
            for file in self.find(entry_path, excludes=excludes):
                files.append(file)
        logger.debug('在%s目录下找到%d个代码文件.', indir, len(files))
        return files


class CodeWriter(object):
    def __init__(
            self, font_name='宋体',
            font_size=10.5, space_before=0.0,
            space_after=2.3, line_spacing=10.5,
            command_chars=None, document=None
    ):
        self.font_name = font_name
        self.font_size = font_size
        self.space_before = space_before
        self.space_after = space_after
        self.line_spacing = line_spacing
        self.command_chars = command_chars if command_chars else DEFAULT_COMMENT_CHARS
        self.document = Document(pkg_resources.resource_filename(
            'swcr', 'template.docx'
        )) if not document else document

    @staticmethod
    def is_blank_line(line):
        """
        判断是否是空行
        """
        return not bool(line)

    def is_comment_line(self, line):
        line = line.lstrip()  # 去除左侧缩进
        is_comment = False
        for comment_char in self.command_chars:
            if line.startswith(comment_char):
                is_comment = True
                break
        return is_comment

    def write_header(self, title):
        """
        写入页眉
        """
        paragraph = self.document.sections[0].header.paragraphs[0]
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = paragraph.add_run(title)
        run.font.name = self.font_name
        run.font.size = Pt(self.font_size)
        return self

    def write_file(self, file):
        """
        把单个文件添加到程序文档里面
        """
        with open(file) as fp:
            for line in fp:
                line = line.rstrip()
                if self.is_blank_line(line):
                    continue
                if self.is_comment_line(line):
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
