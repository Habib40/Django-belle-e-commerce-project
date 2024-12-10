from django import forms
from .models import Review  # Assuming your Review model is in the same app

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['author_name', 'author_email', 'title', 'body', 'rating']  # Specify the fields to include in the form

    # Optionally, you can customize labels and widgets
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['author_name'].label = "Your Name"
        self.fields['author_email'].label = "Your Email"
        self.fields['title'].label = "Review Title"
        self.fields['body'].label = "Body of Review"
        self.fields['rating'].label = "Rating"
        self.fields['rating'].widget = forms.Select(choices=[
            (0, 'Select Rating'),
            (1, '1 Star'),
            (2, '2 Stars'),
            (3, '3 Stars'),
            (4, '4 Stars'),
            (5, '5 Stars'),
        ])