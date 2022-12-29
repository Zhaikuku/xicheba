from django import forms


class RemarksModelForm(forms.ModelForm):
    """
    备注框体大小改动
    """
    remarks = forms.CharField(widget=forms.Textarea, label='备注', required=False)

    class Meta:
        fields = '__all__'
