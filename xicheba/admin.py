from django.contrib import admin
from .models import Users, Materials, Cashier, ExtraProject, EventType
from .models import Choices as Cs
from .form import RemarksModelForm
from django.contrib import messages
# Register your models here.
admin.site.site_title = '洗车吧管理系统'
admin.site.site_header = '洗车吧管理系统'
admin.site.index_title = '管理是一种有意识的行为(✿◡‿◡)'
admin.site.disable_action('delete_selected')
admin.site.empty_value_display = '-'


class CustomAdminAction:
    """
    # 受 Python MRO 顺序,继承时  需要把CustomAdminAction类继承放在第一位
    # 属性查找顺序(找到属性立即中断查找并返回对象)
    # 顺序为__getattribute__() --> instance.__dict__ --> instance.__class__ --> 继承的祖先类(直到object)的__dict__ -->调用 __getattr__()
    """
    # 模型手动注册
    allow_access_class: tuple = ('UsersAdmin', 'CashierAdmin', 'ExtraProjectAdmin')

    def get_class_name(self):
        # 实例的类名
        return self.__class__.__name__

    def has_change_permission(self, request, obj=None):

        if request.user.is_superuser:
            return super().has_change_permission(request, obj)
        elif self.get_class_name() in self.allow_access_class:
            return super().has_add_permission(request)
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return super().has_delete_permission(request, obj)
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return super().has_add_permission(request)
        elif self.get_class_name() in self.allow_access_class:
            return super().has_add_permission(request)
        return False


@admin.register(Users)
class UsersAdmin(CustomAdminAction, admin.ModelAdmin):
    list_display = ('id', 'name', 'sex', 'user_level', 'phone_number', 'member_frequency', 'member_frequency_warning',
                    'create_by_user_name', 'create_time', 'update_time', 'remarks_context',)

    list_display_links = ('name', 'member_frequency_warning')
    search_fields = ['name', 'phone_number']
    list_per_page = 10
    ordering = ('-name',)
    date_hierarchy = 'create_time'
    list_filter = ('user_level',)
    readonly_fields = ['id']
    form = RemarksModelForm
    exclude = ('is_deleted', 'create_by_user',)

    def save_model(self, request, obj, form, change):
        obj.create_by_user = request.user.id
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        非 超级用户 禁止查询逻辑删除的列
        :param request:
        :return:
        """
        if not request.user.is_superuser:
            qs = super().get_queryset(request)
            # 查询属于当前登录用户的出纳明细,并排除逻辑删除的明细
            return qs.filter(create_by_user=request.user.id).exclude(is_deleted=True)
        return super().get_queryset(request)

    def get_list_display(self, request):
        """
        管理员可查看逻辑删除的列
        :param request:
        :return: list_display
        """
        if request.user.is_superuser:
            list_display: tuple = self.list_display + ('is_deleted',)
            return list_display
        return self.list_display


@admin.register(Materials)
class MaterialsAdmin(CustomAdminAction, admin.ModelAdmin):
    list_display = (
        'id', 'id_name', 'brand', 'specifications', 'functions_and_performance', 'number', 'price', 'discount_price',
        'remarks_context',)

    search_fields = ['name']
    list_per_page = 10
    ordering = ('-name',)
    date_hierarchy = 'create_time'
    readonly_fields = ['number', 'id']
    list_filter = ('name',)
    list_display_links = ('id_name',)
    form = RemarksModelForm


@admin.register(Cashier)
class CashierAdmin(CustomAdminAction, admin.ModelAdmin):
    list_display = (
        'id', 'name', 'action', 'number', 'money', 'rewrite_earnings', 'create_by_user_name', 'create_time'
        , 'update_time', 'remarks_context',)
    readonly_fields = ['money', 'id', 'earnings']
    search_fields = ['name']
    list_display_links = ('name', 'rewrite_earnings')
    list_per_page = 10
    date_hierarchy = 'create_time'
    list_filter = ('action', 'name')
    exclude = ('is_deleted', 'create_by_user',)

    form = RemarksModelForm

    def get_list_display(self, request):
        """
        管理员可查看逻辑删除的列
        :param request:
        :return: list_display
        """
        if request.user.is_superuser:
            list_display: tuple = self.list_display + ('is_deleted',)
            return list_display
        return self.list_display

    def get_queryset(self, request):
        """
        非 超级用户 禁止查询逻辑删除的列
        :param request:
        :return:
        """
        if not request.user.is_superuser:
            qs = super().get_queryset(request)
            # 查询属于当前登录用户的出纳明细,并排除已删除的明细
            return qs.filter(create_by_user=request.user.id).exclude(is_deleted=True)
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        """
        计算数量
        :param request:  http 请求头
        :param obj: python 对象
        :param form:  表单
        :param change:  数据库 DML 语言 --> True=update, False=insert
        :return: None
        """
        # 记账类型 == 支出 and 价格类型 != 原价 则保存失败,并弹出 ERROR 级别消息框
        if obj.action == Cs.CashierChoice.outgoing and obj.price_type != Cs.MaterialsPriceType.original_price:
            messages.add_message(request, messages.ERROR, '记账失败：记账类型为支出请选择:原价 < ฅʕ•̫͡•ʔฅ >')
            messages.set_level(request, messages.ERROR)
        else:
            # 获取材料 数量
            # id=obj.name[0] 取材料对应的id 主键 格式为：主键-物料名称 示例：1-玻璃水
            materials_obj = Materials.objects.get(id=obj.name[0])
            # 创建用户 = 当前登录用户id
            obj.create_by_user = request.user.id
            match change:
                # change == True
                case True:
                    # 获取出纳数量
                    cashier_obj = Cashier.objects.get(id=obj.id)
                    cashier_obj_number: int = cashier_obj.number
                    # model 出纳.数量的 绝对值(旧值-新值)
                    # abs 的安全问题
                    differential: int = abs(cashier_obj_number - obj.number)
                    # obj.action 记账类型
                    match obj.action:
                        # 记账类型为收入
                        case Cs.CashierChoice.incoming:
                            if cashier_obj_number > obj.number:
                                materials_obj.number += differential
                            elif cashier_obj_number < obj.number:
                                materials_obj.number -= differential
                        # 记账类型为支出
                        case Cs.CashierChoice.outgoing:
                            if cashier_obj_number > obj.number:
                                materials_obj.number -= differential
                            elif cashier_obj_number < obj.number:
                                materials_obj.number += differential
                        case _:
                            pass
                # change == False
                case False:
                    match obj.action:
                        # 记账类型为收入
                        case Cs.CashierChoice.incoming:
                            # 售价、折扣价格
                            if obj.price_type in (Cs.MaterialsPriceType.price, Cs.MaterialsPriceType.discount_price):
                                # 则材料数 -= 销售数量
                                materials_obj.number -= obj.number
                        #  记账类型为支出
                        case Cs.CashierChoice.outgoing:
                            # 原价
                            if obj.price_type == Cs.MaterialsPriceType.original_price:
                                # 则材料数 += 进货数量
                                materials_obj.number += obj.number
                        case _:
                            pass
                case _:
                    pass
            materials_obj.save()
            super().save_model(request, obj, form, change)


@admin.register(ExtraProject)
class ExtraProjectAdmin(CustomAdminAction, admin.ModelAdmin):
    list_display = (
        'id', 'action', 'number', 'money', 'create_by_user_name', 'create_time', 'update_time', 'remarks_context',)
    list_display_links = ('action',)
    list_per_page = 10
    date_hierarchy = 'create_time'
    search_fields = ['remarks']
    list_filter = ('action',)
    readonly_fields = ['id']
    form = RemarksModelForm
    exclude = ('is_deleted', 'create_by_user',)

    def save_model(self, request, obj, form, change):
        obj.create_by_user = request.user.id
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        非 超级用户 禁止查询逻辑删除的列
        :param request:
        :return:
        """
        if not request.user.is_superuser:
            qs = super().get_queryset(request)
            # 查询属于当前登录用户的出纳明细,并排除已删除的明细
            return qs.filter(create_by_user=request.user.id).exclude(is_deleted=True)
        return super().get_queryset(request)

    def get_list_display(self, request):
        """
        管理员可查看逻辑删除的列
        :param request:
        :return: list_display
        """
        if request.user.is_superuser:
            list_display: tuple = self.list_display + ('is_deleted',)
            return list_display
        return self.list_display


@admin.register(EventType)
class EventTypeAdmin(CustomAdminAction, admin.ModelAdmin):
    list_display = ('id', 'name', 'create_time', 'update_time', 'remarks_context',)
    list_display_links = ('name',)
    list_per_page = 10
    date_hierarchy = 'create_time'
    search_fields = ['name']
    list_filter = ('name',)
    readonly_fields = ('id',)
    form = RemarksModelForm
