from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

from ..models import Question, QuestionCount

def index(request):
    """
    pybo 목록 출력
    """
    # 입력 인자
    page = request.GET.get('page', 1)       #페이지
    kw = request.GET.get('kw', '')          #검색어
    so = request.GET.get('so', 'recent')    #정렬 기준

    #정렬
    if so == 'recommend':
        question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else: #recent
        question_list = Question.objects.order_by('-create_date') #작성일시의 역순
    
    # 조회
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |                  #제목 검색
            Q(content__icontains=kw) |                  #내용 검색
            Q(author__username__icontains=kw) |         #질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)   #답글 글쓴이 검색
        ).distinct()
        
    #페이징 처리
    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so } #page와 kw가 추가됨
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id)
    
    # 조회수
    ip = get_client_ip(request)
    cnt = QuestionCount.objects.filter(ip=ip, question=question).count()
    if cnt == 0:
        qc = QuestionCount(ip=ip, question=question)
        qc.save()
        if question.view_count:
            question.view_count += 1
        else:
            question.view_count = 1
        question.save()
        
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

