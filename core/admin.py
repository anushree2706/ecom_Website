from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Address, Variation


admin.site.site_header = "BIBZ ADMINISTRATION"
admin.site.site_title = "BIBZ ADMIN"
admin.site.index_title = "BIBZ"


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'shipping_address',
                    'payment',
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'payment',
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received']
    search_fields = [
        'user__username',
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'state',
        'zip',
        'default'
    ]
    list_filter = ['default', 'state']  # 'address_type',
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


# admin.site.register(Item)
admin.site.register(Variation)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Address, AddressAdmin)


class InLineLesson(admin.StackedInline):
    model = Variation
    extra = 1
    max_num = 5


class ItemAdmin(admin.ModelAdmin):
    inlines = [InLineLesson]
    list_display = ('title', 'slug', 'price', 'discount_price','label', 'combine_title_and_label',)
    list_display_links = ('title','price', 'discount_price', 'combine_title_and_label',)
    list_editable = ('slug', 'label')
    list_filter = ('title',)
    search_fields = ('title', 'label')
    # fields = ('title',
    #           'price',
    #           'discount_price',
    #           'label',
    #           'slug',
    #           'description',
    #           'image',
    #           'image1',
    #           'image2',
    #           )
    fieldsets = (
         (None, {
            'fields': (
                  'title',
                  'price',
                  'discount_price',
                  'label',
                  'slug',
                  'description',
                  'image',
                  'image1',
                  'image2',
            )
        }
      ),
    )

    def combine_title_and_label(self, obj):
        return f"{obj.title} - {obj.label}"


admin.site.register(Item, ItemAdmin)