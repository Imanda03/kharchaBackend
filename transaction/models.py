from django.db import models
from django.utils.translation import deactivate, ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

User = get_user_model()

class AccountBook(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    user = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE, editable=False)
    created_at = models.DateTimeField(_("Created At"), auto_now=False, auto_now_add=True)
    slug = models.SlugField(_("Slug"), editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            val = self.title
            while(True):
                test = slugify(val)
                count = self.__class__.objects.filter(slug=test).count()
                if(count == 0):
                    break
                val = self.title + " " +str(self.id)
            self.slug = test
        return super().save(*args, **kwargs)

    @property
    def balance(self):
        trans = Transaction.objects.filter(account_book = self.pk)
        debit = trans.filter(_type = "DEBIT").aggregate(sum=models.Sum('amount')).get('sum')
        credit = trans.filter(_type = "CREDIT").aggregate(sum=models.Sum('amount')).get('sum')
        debit = 0 if debit is None else int(debit)
        credit = 0 if credit is None else int(credit)
        return debit-credit

class Transaction(models.Model):
    class Types(models.TextChoices):
        #TYPE_SNTX = TYPE_VALUE, TYPE_NAME
        DEBIT = "DEBIT", "Debit"
        CREDIT = "CREDIT", "Credit"
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    base_type = Types.DEBIT
    amount = models.PositiveIntegerField(_("Amount"))
    description = models.TextField(_("Description"))
    account_book = models.ForeignKey(AccountBook, verbose_name=_(
        "Account Book"), on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, verbose_name=_(
        "Owner"), on_delete=models.CASCADE, null=True)
    _type = models.CharField(
        _("Type"), max_length=50, choices=Types.choices, null=False
    )

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-id']

    def __str__(self):
        return f" {self.amount}"