from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


# Create your models here.


class ToolsBox:
    def remarks_context(self) -> str:
        """
         remarks 备注字符大于30个字符使用省略号替代
        :return: 对象 self 的 remarks 列
        """
        if len(str(self.remarks)) > 10:
            return self.remarks[:10] + '...'
        return self.remarks

    remarks_context.admin_order_field = 'remarks'
    remarks_context.short_description = '备注'

    def id_name(self) -> str:
        """
        :return: 返回 主键 id+name 格式为 14-BLS
        """
        return str(self.id) + '-' + self.name

    id_name.admin_order_field = 'id'
    id_name.short_description = '材料名'

    @classmethod
    def get_values(cls, value: str = None) -> tuple[tuple[str, str]]:
        """
        获取枚举对象
        :param value:   对象 cls 的列名称
        :return: examples (('x','y'),('z', 'm'),)
        """
        try:
            from xpinyin import Pinyin as Py
        except ModuleNotFoundError as notFoundModulePinyin:
            raise ModuleNotFoundError(
                F'NotFound module xpinyin.Pinyin from className={cls.__name__} functionName={cls.get_values.__name__}'
            ) from notFoundModulePinyin
        p = Py()
        data_list: list = list()
        for obj in cls.objects.all():
            val: str = F'obj.{value}'
            vals: str = str(obj.id) + '-' + eval(val)
            key: str = str(obj.id) + '-' + p.get_initials(eval(val), '')
            data_list.append((key, vals))
        return tuple(data_list)

    def create_by_user_name(self) -> str:
        """
        通过 用户 Id 获取 用户名
        :return: last_name + first_name
        """

        user_obj: object = User.objects.get(id=self.create_by_user)
        # user_obj.get_full_name()
        full_name: str = user_obj.last_name + user_obj.first_name
        return full_name or user_obj.id

    create_by_user_name.admin_order_field = 'create_by_user'
    create_by_user_name.short_description = '创建者'


class Choices:
    class IsMembersChoice(models.TextChoices):
        """
        枚举 会员类型
        """
        member = 'member', _('会员')
        not_member = 'not_member', _('非会员')

    class UserGenderChoice(models.TextChoices):
        """
        枚举 性别
        """
        G = 'G', _('男')
        M = 'M', _('女')

    class PaymentMethodsChoice(models.TextChoices):
        """
        枚举 支付方式
        """
        alipay = 'alipay', _('支付宝')
        wechat = 'wechat', _('微信')
        rmb = 'rmb', _('现金')

    class CashierChoice(models.TextChoices):
        """
        枚举 出纳类型
        """
        incoming = 'incoming', _('收入')
        outgoing = 'outgoing', _('支出')

    class MaterialsPriceType(models.TextChoices):
        """
        枚举 出纳管理 记账类型
        """
        original_price = 'original_price', _('原价')
        price = 'price', _('售价')
        discount_price = 'discount_price', _('折扣价')


class Users(models.Model, ToolsBox):
    id = models.BigAutoField(primary_key=True, verbose_name='ID', help_text='自动增长')
    name = models.CharField(max_length=20, verbose_name='客户名称')
    sex = models.CharField(choices=Choices.UserGenderChoice.choices, max_length=1, default=Choices.UserGenderChoice.G,
                           verbose_name='客户性别')
    user_level = models.CharField(choices=Choices.IsMembersChoice.choices, max_length=10,
                                  default=Choices.IsMembersChoice.not_member,
                                  verbose_name='客户等级')
    phone_number = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号码')
    make_collections = models.IntegerField(default=0, verbose_name='已收会员款')
    payment_methods = models.CharField(max_length=10, choices=Choices.PaymentMethodsChoice.choices,
                                       default=Choices.PaymentMethodsChoice.wechat, verbose_name='支付方式')
    member_frequency = models.IntegerField(default=0, verbose_name='会员价次数')
    using_frequency = models.IntegerField(default=0, verbose_name='消费次数', help_text='每消费一次加一')
    remarks = models.CharField(max_length=100, blank=True, null=True, verbose_name='备注', help_text='100字以内的备注内容')
    create_by_user = models.IntegerField(default='0', verbose_name='创建用户')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def delete(self, using=None, keep_parents=False):
        # 逻辑删除
        self.is_deleted = True
        self.save()

    def member_frequency_warning(self) -> int:
        """
        会员价洗车次数 > 剩余次数 return 剩余次数有误
        剩余次数 <= 0 return 剩余次数0
        会员价洗车次数 ==  剩余次数 return 消费次数已用完
        :return: 对象 self 的 using_frequency 列
        """
        if self.user_level == Choices.IsMembersChoice.member:
            if self.using_frequency <= 0:
                return format_html('<span style="color: green;">{}</span>', '消费次数0')
            elif self.using_frequency == self.member_frequency:
                return format_html('<span style="color: red;">{}</span>', '消费次数已用完')
            elif self.using_frequency > self.member_frequency:
                return format_html('<span style="color: red;">{}</span>', '消费次数有误')
        return self.using_frequency

    member_frequency_warning.admin_order_field = 'using_frequency'
    member_frequency_warning.short_description = '消费次数'

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "客户明细"
        verbose_name_plural = "客户管理"


class Materials(models.Model, ToolsBox):
    id = models.BigAutoField(primary_key=True, verbose_name='ID', help_text='自动增长')
    name = models.CharField(max_length=15, verbose_name='材料名')
    specifications = models.CharField(max_length=15, blank=True, null=True, verbose_name='规格')
    original_price = models.IntegerField(default=0, verbose_name='原价')
    price = models.IntegerField(default=0, verbose_name='售价')
    discount_price = models.IntegerField(default=0, verbose_name='折扣价')
    number = models.IntegerField(default=0, verbose_name='数量', help_text='由出纳管理自动记数')
    brand = models.CharField(max_length=10, blank=True, verbose_name='品牌名')
    functions_and_performance = models.CharField(max_length=20, blank=True, null=True, verbose_name='功能')
    remarks = models.CharField(max_length=100, blank=True, null=True, verbose_name='备注', help_text='100字以内的备注内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self) -> str:
        return str(self.id) + '-' + self.name

    class Meta:
        verbose_name = '材料明细'
        verbose_name_plural = '材料管理'


class Cashier(models.Model, ToolsBox):
    def __init__(self, *args, **kwargs):
        """
        动态获取材料名
        """
        self.materials = Materials
        super().__init__(*args, **kwargs)
        self._meta.get_field('name').choices = Materials.get_values(value='name')

    id = models.BigAutoField(primary_key=True, verbose_name='ID', help_text='自动增长')
    name = models.CharField(max_length=30, choices=Materials.get_values(value='name'), default='', verbose_name='物品名称')
    action = models.CharField(choices=Choices.CashierChoice.choices, max_length=10, verbose_name="记账类型")
    number = models.IntegerField(default=0, verbose_name='数量', help_text='自动记数到材料管理')
    price_type = models.CharField(max_length=20, choices=Choices.MaterialsPriceType.choices, verbose_name='价格类型',
                                  help_text='记账类型为支出请选择: 原价 < ฅʕ•̫͡•ʔฅ > 记账类型为收入请选择：售价或者折扣价')
    money = models.IntegerField(default=0, verbose_name='总金额', help_text='总价格自动计算')
    earnings = models.IntegerField(default=0, verbose_name='收益', help_text='收益自动计算')
    remarks = models.CharField(max_length=100, blank=True, null=True, verbose_name='备注', help_text='100字以内的备注内容')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    create_by_user = models.IntegerField(default='0', verbose_name='创建用户')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def delete(self, using=None, keep_parents=False):
        # 逻辑删除
        if not self.is_deleted:
            self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs) -> None:
        """
         提交保存数据时,根据记账类型 计算总价格以及收益
        :param args:
        :param kwargs:
        :return:
        """
        # 实例化材料对象
        materials_obj = self.materials.objects.get(id=self.name[0])
        match self.action:
            # 记账类型为收入
            case Choices.CashierChoice.incoming:
                # 计算价格(售价、折扣价格)
                # 如果使用原价作为收入类型则收益为 0
                if self.price_type in (Choices.MaterialsPriceType.price, Choices.MaterialsPriceType.discount_price):
                    val = F'materials_obj.{self.price_type}'
                    self.money = self.number * eval(val)
                    # 计算收益
                    #self.earnings = (self.number * eval(val)) - (self.number * materials_obj.original_price)
                    self.earnings = (eval(val) - materials_obj.original_price) * self.number
            case Choices.CashierChoice.outgoing:
                # 计算价格(原价)
                if self.price_type == Choices.MaterialsPriceType.original_price:
                    self.money = self.number * materials_obj.original_price
            # 上述处理完毕,保存 Materials 对象
        materials_obj.save()
        # 上述处理完毕,保存 Cashier 对象
        super().save(*args, **kwargs)

    def rewrite_earnings(self) -> format_html:
        match self.action:
            case Choices.CashierChoice.incoming:
                if self.price_type == Choices.MaterialsPriceType.original_price and self.earnings == 0:
                    return format_html('<span style="color: green;">{}</span>', '原价出售')
                elif self.earnings == 0:
                    return format_html('<span style="color: green;">{}</span>', '暂无收益')
                elif self.earnings <= 0:
                    return format_html('<span style="color: read;">{}</span>', '亏本')
            case Choices.CashierChoice.outgoing:
                return format_html('<span style="color: blue;">{}</span>', '<---')
            case _:
                return format_html('<span style="color: blue;">{}</span>', '请联系开发人员')
        return format_html('<span style="color: green;">{}</span>', self.earnings)

    rewrite_earnings.admin_order_field = 'earnings'
    rewrite_earnings.short_description = '收益'

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = '出纳明细'
        verbose_name_plural = '出纳管理'


class EventType(models.Model, ToolsBox):
    id = models.BigAutoField(primary_key=True, verbose_name='ID', help_text='自动增长')
    name = models.CharField(max_length=30, verbose_name='事件类型')
    remarks = models.CharField(max_length=100, blank=True, null=True, verbose_name='备注', help_text='100字以内的备注内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = '事件明细'
        verbose_name_plural = '事件管理'


class ExtraProject(models.Model, ToolsBox):
    id = models.BigAutoField(primary_key=True, verbose_name='ID', help_text='自动增长')
    action = models.CharField(choices=EventType.get_values(value='name'), default='', max_length=30,
                              verbose_name="事件类型")
    number = models.IntegerField(default=0, verbose_name='次数')
    money = models.IntegerField(default=0, verbose_name='总金额')
    remarks = models.CharField(max_length=100, blank=True, null=True, verbose_name='备注', help_text='100字以内的备注内容')
    create_by_user = models.IntegerField(default='0', verbose_name='创建用户')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def delete(self, using=None, keep_parents=False):
        # 逻辑删除
        self.is_deleted = True
        self.save()

    class Meta:
        verbose_name = '散项明细'
        verbose_name_plural = '散项管理'

    def __str__(self) -> str:
        return self.action
