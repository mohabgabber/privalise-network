from django import template

register = template.Library()

@register.filter(name="add_classes")
def add_classes(value, arg):
  classes = value.field.widget.attrs.get("class", "")

  if classes:
      classes = classes.split(" ")
  else:
      classes = []

  new_classes = arg.split(" ")
  for c in new_classes:
      if c not in classes:
          classes.append(c)

  return value.as_widget(attrs={"class": " ".join(classes)})

@register.filter(name="add_placeholder")
def add_placeholder(value, arg):
    # print(value.field.widget.attrs)
    return value.as_widget(attrs={"placeholder": arg})