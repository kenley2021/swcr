# swcr：计算机软件著作权程序鉴别材料（即源代码）生成器

目录
=================

  * [安装](#安装)
  * [背景](#背景)
  * [使用](#使用)
     * [程序鉴别材料要求](#程序鉴别材料要求)
     * [如何实现每页50行](#如何实现每页50行)
     * [参数](#参数)
     * [示例](#示例)
        * [克隆代码](#克隆代码)
        * [生成文档](#生成文档)
     * [常见问题](#常见问题)
        * [如何指定页眉？](#如何指定页眉？)
        * [如何添加其他格式的代码？](#如何添加其他格式的代码？)
        * [如何排除指定文件或文件夹？](#如何排除指定文件或文件夹？)
        * [如何调整默认的注释风格？](#如何调整默认的注释风格？)
        * [如何调整字体？](#如何调整字体？)
        * [虽然我知道默认的字体、字号、段前间距、段后间距、行间距可以实现每页50行，但是我还是想调整，怎么办？](#虽然我知道默认的字体、字号、段前间距、段后间距、行间距可以实现每页50行，但是我还是想调整，怎么办？)
        * [能不能输出查找文件的详细过程呢？](#能不能输出查找文件的详细过程呢？)

## 安装

```shell script
pip install swcr
```

## 背景

工作中需要申请软件著作权，软件著作权需要提供以下材料：

1. 申请表：可以在官网通过网页生成
2. 身份证明：企业的话一般就是营业执照
3. 程序鉴别材料：一般就是源代码整理出的PDF文件
4. 文档鉴别材料：一般就是该软件的操作手册

申请表身份证明比较好准备，文档鉴别材料则必须手写，`swcr`则用于生成程序鉴别材料。目前支持如下功能：

1. 指定多个源代码目录
2. 指定多中注释风格
3. 指定字体、字号、段前间距、段后间距、行距
4. 排除特定文件、文件夹

## 使用

### 程序鉴别材料要求

1. 每页至少50行
2. 不能含有注释、空行
3. 页眉部分必须包含软件名称、版本号、页码（软件名+版本号居中，页码右侧对齐）

### 如何实现每页50行

上述3点，第2、3两点比较好实现，第1点我通过测试发现，当：

1. 字号为10.5pt
2. 行间距为10.5pt
3. 段前间距为0
4. 段后间距为2.3pt

时，刚好实现每页50行。

### 参数

```
Usage: swcr [OPTIONS]

Options:
  -t, --title TEXT            软件名称+版本号，默认为软件著作权程序鉴别材料生成器V1.0，此名称用于生成页眉
  -i, --indir PATH            源码所在文件夹，可以指定多个，默认为当前目录
  -e, --ext TEXT              源代码后缀，可以指定多个，默认为Python源代码
  -c, --comment-char TEXT     注释字符串，可以指定多个，默认为#、//
  --font-name TEXT            字体，默认为宋体
  --font-size FLOAT RANGE     字号，默认为五号，即10.5号
  --space-before FLOAT RANGE  段前间距，默认为0
  --space-after FLOAT RANGE   段后间距，默认为2.3
  --line-spacing FLOAT RANGE  行距，默认为固定值10.5
  --exclude PATH              需要排除的文件或路径，可以指定多个
  -o, --outfile PATH          输出文件（docx格式），默认为当前目录的code.docx
  -v, --verbose               打印调试信息
  --help                      Show this message and exit.
```

### 示例

下面以[django-guardian项目](https://github.com/django-guardian/django-guardian)为例来说明`swcr`的用法。

#### 克隆代码

```shell script
git clone git@github.com:django-guardian/django-guardian.git
```

#### 生成文档

```shell script
swcr -i django-guardian -o django-guardian.docx
```

### 常见问题

#### 如何指定页眉？

```shell script
swcr -i django-guardian -t django-guardian -o django-guardian.docx
```

#### 如何添加其他格式的代码？

上述方法只能识别Python源码，如果需要识别html、css、js代码，可以指定`-e`参数。

```shell script
swcr -i django-guardian \
    -t django-guardian \
    -e py -e html -e js \
    -o django-guardian.docx
```

#### 如何排除指定文件或文件夹？

```shell script
swcr -i django-guardian \
    -t django-guardian \
    --exclude django-guardian/contrib/ \
    --exclude django-guardian/docs/ \
    --exclude django-guardian/benchmarks/ \
    --exclude django-guardian/example_project/ \
    -o django-guardian.docx
```

#### 如何调整默认的注释风格？

默认情况下，`swcr`把以`#`、`//`开头的行作为注释行删除，例如我想删除以`"""`开头的行（Python另一种注释风格）：

```shell script
swcr -i django-guardian \
    -t django-guardian \
    -c '#' -c '//' -c '"""' \
    -o django-guardian.docx
```

注意，`swcr`目前不支持删除多行注释。

#### 如何调整字体？

`swcr`默认使用宋体，如果需要调整可以使用`--font-name`参数。

```shell script
swcr -i django-guardian \
    -t django-guardian \
    --font-name menlo \
    -o django-guardian.docx
```

#### 虽然我知道默认的字体、字号、段前间距、段后间距、行间距可以实现每页50行，但是我还是想调整，怎么办？

```shell script
swcr -i django-guardian \
    -t django-guardian \
    --font-name menlo \
    --font-size 12 \
    --space-before 1 \
    --space-after 5 \
    --line-spacing 12 \
    -o django-guardian.docx
```

#### 能不能输出查找文件的详细过程呢？

```shell script
swcr -i django-guardian -o django-guardian.docx -v
```

```
...
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/posts/templates/posts目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/posts/templates目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/posts目录下找到8个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/core/migrations目录下找到3个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/core目录下找到7个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/articles/migrations目录下找到3个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/articles/templates/articles目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/articles/templates目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/articles目录下找到10个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/static/css目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/static/js目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/static/img目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/static目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project/templates目录下找到0个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian/example_project目录下找到29个代码文件.
DEBUG:swcr.swcr:在/Users/dev/Temp/django-guardian目录下找到94个代码文件.
```
