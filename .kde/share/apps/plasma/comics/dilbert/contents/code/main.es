/*
 *   Copyright (C) 2007 Tobias Koenig <tokoe@kde.org>
 *   Copyright (C) 2010 Matthias Fuchs <mat69@gmx.net>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU Library General Public License version 2 as
 *   published by the Free Software Foundation
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details
 *
 *   You should have received a copy of the GNU Library General Public
 *   License along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

function init()
{
    comic.comicAuthor = "Scott Adams";
    comic.firstIdentifier = "1994-01-01";
    comic.websiteUrl = "http://dilbert.com/strips/comic/" + comic.identifier.toString(date.ISODate) + "/";

    var url = "http://dilbert.com/fast/" + comic.identifier.toString(date.ISODate) + "/";
    var infos = {
        "User-Agent": "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.6 (like Gecko)",
        "Accept": "text/html, image/jpeg, image/png, text/*, image/*, */*",
        "Accept-Encoding": "functionlate",
        "Accept-Charset": "iso-8859-15, utf-8;q=0.5, *;q=0.5",
        "Accept-Language": "en",
        "Host": "dilbert.com",
        "Connection": "Keep-Alive"
    }
    
    //if today is selected find the most current strip on the website (might also be yesterday)
    if (comic.identifier.toString() == date.currentDate().toString()) {
        comic.requestPage("http://dilbert.com/fast/", comic.User, infos);
    } else {
        comic.requestPage(url, comic.Page, infos);
    }
}

function getComic(data)
{
    var re = new RegExp("<img src=\"(/dyn/str_strip/[0-9/]+/[0-9]+\\.strip)(\\.print)(\\.gif)\"");
    var match = re.exec(data);

    if (match != null) {
        url = "http://dilbert.com/" + match[1] + ".zoom" + match[3];
        comic.requestPage(url, comic.Image);
    } else {
        comic.error();
    }
}

function pageRetrieved(id, data)
{
    //look at the most recent comic
    if (id == comic.User) {
        var re = new RegExp("<a href=\"/fast/(\\d{4}-\\d{2}-\\d{2})/\"><img src=\"/img/v1/blog/btn\\.left_arrow\\.gif\"");
        var match = re.exec(data);
        if (match != null) {
            var temp = 
            comic.lastIdentifier = date.fromString(match[1], "yyyy-MM-dd").addDays(1);//last is previous + 1
            comic.websiteUrl = "http://dilbert.com/strips/comic/" + comic.identifier.toString(date.ISODate) + "/";
            getComic(data);
        } else {
            comic.error();
        }
    }
    if (id == comic.Page) {
        getComic(data);
    }
}
