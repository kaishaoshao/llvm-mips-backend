---
title: LLVM backend resources
description: Talks, blogs, slides on LLVM backend structures.
---

Official LLVM backend guide: https://llvm.org/docs/WritingAnLLVMBackend.html


Slides on Selection DAG: https://llvm.org/devmtg/2024-10/slides/tutorial/MacLean-Fargnoli-ABeginnersGuide-to-SelectionDAG.pdf

Slides on building an LLVM Backend, has all the basics.
https://llvm.org/devmtg/2014-04/PDFs/Talks/Building%20an%20LLVM%20backend.pdf

A guide just like this one.
https://sourcecodeartisan.com/2020/09/13/llvm-backend-0.html

Detailed guide https://jonathan2251.github.io/lbd/TutorialLLVMBackendCpu0.pdf
The ebook version: https://jonathan2251.github.io/lbt/index.html

**From [this llvm thread](https://groups.google.com/g/llvm-dev/c/aJCR1mBC0So/m/yZipPTzTCAAJ)**
> "Lessons in TableGen"
> FOSDEM 2019; Nicolai Hähnle
> https://fosdem.org/2019/schedule/event/llvm_tablegen/
> Slides:
> https://archive.fosdem.org/2019/schedule/event/llvm_tablegen/attachments/slides/3304/export/events/attachments/llvm_tablegen/slides/3304/tablegen.pdf
> 
> Series:
> - What has TableGen ever done for us?:
> http://nhaehnle.blogspot.com/2018/02/tablegen-1-what-has-tablegen-ever-done.html
> - Functional Programming:
> http://nhaehnle.blogspot.com/2018/02/tablegen-2-functional-programming.html
> - Bits: http://nhaehnle.blogspot.com/2018/02/tablegen-3-bits.html
> - Resolving variables:
> http://nhaehnle.blogspot.com/2018/03/tablegen-4-resolving-variables.html
> - DAGs: http://nhaehnle.blogspot.com/2018/03/tablegen-5-dags.html
> 
> Some of the parts of TableGen used in SelectionDAG are in the backend
> docs (e.g., the keywords OP asked about):
> https://llvm.org/docs/WritingAnLLVMBackend.html#instruction-set
> & https://llvm.org/docs/WritingAnLLVMBackend.html#instruction-selector
> (has a simple example of `PatFrag` for `store`).
> 
> There are a few examples of simple .td files an LLVM backend in the
> following:
> 
> LLVM backend development by example (RISC-V)
> 2018 LLVM Developers’ Meeting; Alex Bradbury
> https://www.youtube.com/watch?v=AFaIP-dF-RA
> 
> 2014 - Building an LLVM Backend - LLVM Developer's Meeting
> https://llvm.org/devmtg/2014-10/#tutorial1
> https://llvm.org/devmtg/2014-10/Slides/Cormack-BuildingAnLLVMBackend.pdf
> https://llvm.org/devmtg/2014-04/PDFs/Talks/Building%20an%20LLVM%20backend.pdf
> http://web.archive.org/http://llvm.org/devmtg/2014-10/Videos/Building%20an%20LLVM%20backend-720.mov
> http://llvm.org/devmtg/2014-10/#tutorial1
> http://www.inf.ed.ac.uk/teaching/courses/ct/other/LLVMBackend-2015-03-26_v2.pdf
> 
> llvm-leg: LEG Example Backend
> LEG Example Backend: a simple example LLVM backend for an ARM-like
> architecture: 'LEG'.
> https://github.com/frasercrmck/llvm-leg

## Others
Dealing with register hierarchies https://llvm.org/devmtg/2016-11/Slides/Braun-DealingWithRegisterHierarchies.pdf