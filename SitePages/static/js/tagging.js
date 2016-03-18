/*
 * Add Tag System
 * A PEN BY Mac Carrithers
 * http://codepen.io/easymac/pen/azqVgq
 */

// Notice: Currently tagging.js is only used on meter-list page.
//         Some id selectors are directly related to elements
//         on that page.
//         Thus, some universalize adaptions need to be implemented
//         for its further use on other pages.

$(document).ready(function () {
    tagger_handle = new Tagger();
});

function Tagger() {
    this.tags = [];
    var tags = $('#tags');

    this.addTag = function (tag) {
        if (this.tags.indexOf(tag) > -1) {
            $('#tags span[data-tag="' + tag + '"]').shake();return;
        }
        this.tags.push(tag);
        tags.append('<span data-tag="' + tag + '">' + tag + '<i class="fa fa-times" data-tag="' + tag + '"></i></span>')
    };

    this.removeTag = function (tag) {
        var index = this.tags.indexOf(tag);
        if (index > -1) {
            this.tags.splice(index, 1);
        }

        var tagEl = $('#tags span[data-tag="' + tag + '"]');
        tagEl.addClass('deleting');
        setTimeout(function () {
            tagEl.remove();
        }, 500)
    };

    this.removeTagCallBack = function(){
    };

    this.init = function () {
        var self = this;
        tags.delegate("i", "click", function () {
            var tag = $(this).data('tag');
            self.removeTag(tag);
            self.removeTagCallBack(tag);
        })
    };
    this.init();
}

jQuery.fn.shake = function () {
    var el = this;
    el.addClass('shake');
    el.removeClass('notShake');
    setTimeout(function () {
        el.addClass('notShake');
        el.removeClass('shake');
    }, 500);
};

// selectText from Tom Oakley
// @ http://stackoverflow.com/questions/12243898/how-to-select-all-text-in-contenteditable-div
jQuery.fn.selectText = function () {
    var doc = document;
    var element = this[0];
    if (doc.body.createTextRange) {
        var range = document.body.createTextRange();
        range.moveToElementText(element);
        range.select();
    } else if (window.getSelection) {
        var selection = window.getSelection();
        var range = document.createRange();
        range.selectNodeContents(element);
        selection.removeAllRanges();
        selection.addRange(range);
    }
};