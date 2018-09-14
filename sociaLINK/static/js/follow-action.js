function followAction(token, padding, paddingRight) {
    //Send follow request AJAX
    $(".follow-btn").each((index) => {
        let followBtn = $(".follow-btn").eq(index);
        //Code to change state when hover on unfollow button
        $(document).ready(() => {
            followBtn.mouseenter(() => {
                if (followBtn.hasClass("stop-following"))
                {
                    followBtn.html("Stop Following");
                    followBtn.css("padding", `${padding}px`);
                }
            });

            followBtn.mouseleave(() => {
                if (followBtn.hasClass("stop-following"))
                {  
                    followBtn.css("padding-right", `${paddingRight}px`);
                    followBtn.html(`Following <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="white" d="M173.898 439.404l-166.4-166.4c-9.997-9.997-9.997-26.206 0-36.204l36.203-36.204c9.997-9.998 26.207-9.998 36.204 0L192 312.69 432.095 72.596c9.997-9.997 26.207-9.997 36.204 0l36.203 36.204c9.997 9.997 9.997 26.206 0 36.204l-294.4 294.401c-9.998 9.997-26.207 9.997-36.204-.001z"/></svg>`);
                }
            });
        });
        followBtn.click(() => {
            let userId = followBtn.attr("id").split("-")[2];
            $.ajax({
                type:"post",
                data: {
                    "follow": userId,
                    csrfmiddlewaretoken: token,
                }
            }).done((data) => {
                data = JSON.parse(data);
                if (data["followed"] == "False") {
                    followBtn.removeClass("stop-following");
                    followBtn.html("Follow");
                    followBtn.attr("title", "Follow {{ targetUser.get_full_name }}");
                }
                else if (data["followed"] == "True") {
                    followBtn.addClass("stop-following");
                    followBtn.html(`Following <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="white" d="M173.898 439.404l-166.4-166.4c-9.997-9.997-9.997-26.206 0-36.204l36.203-36.204c9.997-9.998 26.207-9.998 36.204 0L192 312.69 432.095 72.596c9.997-9.997 26.207-9.997 36.204 0l36.203 36.204c9.997 9.997 9.997 26.206 0 36.204l-294.4 294.401c-9.998 9.997-26.207 9.997-36.204-.001z"/></svg>`);
                    followBtn.attr("title", "Stop following {{ targetUser.get_full_name }}");
                }
                $(".statistic").html(`Followers: ${data['followers']}, Followings: ${data['followings']}`);
            });
        });
    });
}