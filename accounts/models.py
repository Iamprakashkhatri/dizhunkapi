import random
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    firebase_uuid = models.CharField(max_length=200, blank=True, default='')
    display_name = models.CharField(max_length=50,blank=True,default='')
    profile_image = models.ImageField(upload_to='profile_images/', null=True)
    referral_code = models.CharField(default='',max_length=300,blank=True)
    push_notification = models.BooleanField(default=True)
    twitter = models.CharField(max_length=200, blank=True, default='')
    facebook = models.CharField(max_length=200, blank=True, default='')
    instagram = models.CharField(max_length=200, blank=True, default='')
    gender = models.CharField(max_length=30,default='',blank=True,null=True)
    dob = models.DateField(blank=True,null=True)
    nationality = models.CharField(max_length=100,blank=True,null=True,default='')
    users_referred = models.ManyToManyField('self')
    total_earning = models.IntegerField(default=0)
    is_teacher = models.BooleanField(default=False)
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('user')

    def generate_referral_code(self):
        def _generate_code():
            t = "abcdefghijkmnopqrstuvwwxyzABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890"
            return "".join([random.choice(t) for i in range(40)])

        code = _generate_code()
        while User.objects.filter(referral_code=code).exists():
            code = _generate_code()
        return code

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.referral_code = self.generate_referral_code()
        elif not self.referral_code:
            self.referral_code = self.generate_referral_code()
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ' '
        return url
