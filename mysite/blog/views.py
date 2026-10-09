# from importlib.metadata import pass_none
from django.contrib.auth.models import User
from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q,F
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import  Http404
from blog.models import Articles,Member,Comments
from PIL import Image
from django.contrib import messages


#文章展示加首页
@login_required(login_url='blog:login')
def index(request):
    keywords = request.GET.get('keywords')
    if keywords:
        artis = Articles.objects.filter(
            Q(title__icontains=keywords) | Q(author__nickname__icontains=keywords),
            is_published=True,
        )
    else:
        artis = Articles.objects.filter(is_published=True)

    return render(request,'index.html',{'artis':artis, "keywords": keywords})


@login_required(login_url='blog:login')#反复烘烤
def members(request,pk=None):
    member = get_object_or_404(Member,pk=pk)if pk else request.user.member
    keywords = request.GET.get('keywords')
    is_self = (pk is None) or (request.user.member.pk == pk)
    if is_self:
        artis = Articles.objects.filter(author=member)
    else:
        artis = Articles.objects.filter(author=member, is_published=True)

    if keywords:
        members_list = Member.objects.filter(
            nickname__icontains=keywords
        )
    else:
        members_list = Member.objects.none()

    return render(request,'members.html',{'artis':artis, "keywords": keywords,'members_list':members_list,'member':member})


#占位页：小游戏/个人中心/关于作者/头像/搜索 等未实现功能统一跳转
def placeholder(request):
    return render(request,'placeholder.html')


def login_register(request):#我喜欢简便的登录注册
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if  User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user is None:
                return render(request,'login.html',{'ERROR':'密码错误'})

        else:
            if len(username) > 18:
                return render(request, 'login.html', {
                    'ERROR': '昵称不能超过 18 个字',
                })
            user = User.objects.create_user(username=username,password=password)
            Member.objects.create(user=user,nickname=username)

        login(request,user)
        return redirect('blog:index')
    return render(request,'login.html')


@login_required(login_url='blog:login')
def logout_view(request):
    logout(request)
    return redirect("blog:login")


@login_required(login_url='blog:login')
def article_detail(request, pk):
    article = get_object_or_404(Articles,pk=pk)
    if not article.is_published and request.user.member != article.author:
        raise Http404()
    Articles.objects.filter(pk=pk).update(views=F("views") + 1)
    article.refresh_from_db()
    return render(request,'article_detail.html',{'article':article})
'''这里我的理解是，读加改读取'加'的参照物需要额外的时间，而F不需要。原子性是从较根本的地方改数据所以必须得一个一个改。
就像两个人发消息告诉你‘你得比昨天的数据多加一’（那两条消息同一天到就完了）和两个人排着队堵在你家门口,每人来一句‘现在马上让数据多加一我看着你加完再走’
的区别一样
'''


@login_required(login_url='blog:login')
def add_comment(request, pk):
    article = get_object_or_404(Articles,pk=pk)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comments.objects.create(
                content=content,
                article=article,
                commenter=request.user.member,   # 从登录用户拿
            )
        return redirect("blog:article_detail", pk=pk)
    return redirect("blog:article_detail", pk=pk)


@login_required(login_url='blog:login')
def submit(request):
    if request.method == "GET":
        return render(request,'submit.html')
    #卡壳 这里留一份之前的老写法代码

    title = request.POST.get('title')
    content = request.POST.get('content')
    toggle = request.POST.get('toggle')

    if title and content:
        if len(title) > 30:
            return render(request, 'submit.html', {
                'ERROR': '标题不能超过 30 个字',
                'title': title,
                'content': content
            })
        article = Articles.objects.create(author=request.user.member, title=title, content=content)

        if toggle:
            article.is_published = True
            article.save()
            return redirect('blog:index')

        return redirect('blog:members')

    else:
        return render(request,'submit.html',{
                                             'ERROR':'标题和正文均必填',
                                             'title':title,
                                             'content':content
                                             })



@login_required(login_url='blog:login')#狂改。
def edit_article(request,pk):
    article = get_object_or_404(Articles, pk=pk,author=request.user.member)

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        toggle = request.POST.get('toggle')
        delete = request.POST.get('delete')

        if not(title and content):
            return render(request, 'edit.html', {
                'ERROR': '标题和正文均必填',
                'title': title,
                'content': content
            })
        if len(title) > 30:
            return render(request, 'edit.html', {
                'ERROR': '标题不能超过 30 个字',
                'title': title,
                'content': content
            })

        if delete:
            article.delete()
            return redirect("blog:members", pk=request.user.member.pk)

        if toggle:
            article.is_published = True

        article.title = title
        article.content = content
        article.save()

        return redirect("blog:members", pk=request.user.member.pk)

    return render(request, "edit.html", {"article": article})


@login_required(login_url='blog:login')
def edit_member(request):
    member = request.user.member

    if request.method == "POST":
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        bio = request.POST.get('bio')

        if nickname or email or bio:

            if nickname:
                # 别人占用了这个名字才拦（排除自己）(deepseek修改建议)
                if User.objects.filter(username=nickname).exclude(pk=request.user.pk).exists():
                    # 重名了，别存，回表单给个提示
                    return render(request, "edit_member.html", {
                        'member': member,
                        "ERROR": "这个用户名已被占用",
                    })
                if len(nickname) >18:
                    return render(request, 'edit_member.html', {
                        'member': member,
                        'ERROR': '昵称不能超过 18 个字',
                    })
                
                member.nickname = nickname
                request.user.username = nickname
                request.user.save()

            member.email = email
            member.bio = bio
            member.save()
        return redirect("blog:members")

    return render(request, "edit_member.html", {"member": member})


#这段先抄了，晚点来详细搞懂
@login_required(login_url="blog:login")
def upload_avatar(request):
    if request.method == "POST":
        avatar = request.FILES.get("avatar")   # ← 从 FILES 取，不是 POST
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                messages.error(request, "头像不能超过 2MB")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

                #检查像素尺寸
            try:
                img = Image.open(avatar)
                w, h = img.size
            except Exception:
                messages.error(request, "这不是合法图片")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

            if w < 50 or h < 50:
                messages.error(request, "头像至少 50x50 像素")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))
            if w > 2000 or h > 2000:
                messages.error(request, "头像不能超过 2000x2000 像素")
                return redirect(request.META.get("HTTP_REFERER", "blog:index"))

            member = request.user.member
            avatar.seek(0)
            member.avatar = avatar
            member.save()
    return redirect(request.META.get("HTTP_REFERER", "blog:index"))