//Trim whitespace head and end of posts
function TrimContent() {
    $(".post-content").each((index, value) => {
        let content = $(".post-content").eq(index).html();
        if(content == null) return content;
        content = content.trim();
        $(".post-content").eq(index).html(content);
    });
}

//Handle the page scroll to load more posts using AJAX
function pageScrollAjax(url, token) {
    $(window).scroll(function() {
    if($(window).scrollTop() + $(window).height() == $(document).height()) {
        // Only show load more icon when the no more post message isn't showing
        if ($("#no-more-posts").length == 0)
            $(".load-more").css("display", "initial");
        //Set 1s for page load, just to make it look cool
        setTimeout(() => {
            numberOfLoad++;
            $.ajax({
                type: "post",
                url: url,
                data: {
                    numberOfLoad: numberOfLoad,
                    csrfmiddlewaretoken: token,
                }
            }).done((data) => {
                data = JSON.parse(data);
                //Receive JSON data and pass it to the view
                if (data[0] != undefined) {
                for(let i = 0; i < data.length; i++) {
                    let content = data[i].fields.content.replace(/\u21B5/g,'<br/>');
                    //Add post content
                    let post = `<div class="post-detail">
                            <img class="post-avatar" src="${data[i].avatar}">
                            <p class="post-user-name"><a href = "${data[i].slug}">${data[i].username}</a></p>
                            <div class="post-wrap">
                            <div class="post-content">
                                ${content}
                            </div>
                            <div class="post-footer">
                                <p hidden id="${data[i].pk}">${data[i].pk}</p> 
                                <svg id="up-${data[i].pk}" class="post-action up" aria-hidden="true" data-prefix="fas" data-icon="thumbs-up" class="svg-inline--fa fa-thumbs-up fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="green" d="M104 224H24c-13.255 0-24 10.745-24 24v240c0 13.255 10.745 24 24 24h80c13.255 0 24-10.745 24-24V248c0-13.255-10.745-24-24-24zM64 472c-13.255 0-24-10.745-24-24s10.745-24 24-24 24 10.745 24 24-10.745 24-24 24zM384 81.452c0 42.416-25.97 66.208-33.277 94.548h101.723c33.397 0 59.397 27.746 59.553 58.098.084 17.938-7.546 37.249-19.439 49.197l-.11.11c9.836 23.337 8.237 56.037-9.308 79.469 8.681 25.895-.069 57.704-16.382 74.757 4.298 17.598 2.244 32.575-6.148 44.632C440.202 511.587 389.616 512 346.839 512l-2.845-.001c-48.287-.017-87.806-17.598-119.56-31.725-15.957-7.099-36.821-15.887-52.651-16.178-6.54-.12-11.783-5.457-11.783-11.998v-213.77c0-3.2 1.282-6.271 3.558-8.521 39.614-39.144 56.648-80.587 89.117-113.111 14.804-14.832 20.188-37.236 25.393-58.902C282.515 39.293 291.817 0 312 0c24 0 72 8 72 81.452z"></path></svg><span class="action-number">${data[i].fields.upNumber} </span>
                                <svg id="down-${data[i].pk}" class="post-action down" aria-hidden="true" data-prefix="fas" data-icon="thumbs-down" class="svg-inline--fa fa-thumbs-down fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="red" d="M0 56v240c0 13.255 10.745 24 24 24h80c13.255 0 24-10.745 24-24V56c0-13.255-10.745-24-24-24H24C10.745 32 0 42.745 0 56zm40 200c0-13.255 10.745-24 24-24s24 10.745 24 24-10.745 24-24 24-24-10.745-24-24zm272 256c-20.183 0-29.485-39.293-33.931-57.795-5.206-21.666-10.589-44.07-25.393-58.902-32.469-32.524-49.503-73.967-89.117-113.111a11.98 11.98 0 0 1-3.558-8.521V59.901c0-6.541 5.243-11.878 11.783-11.998 15.831-.29 36.694-9.079 52.651-16.178C256.189 17.598 295.709.017 343.995 0h2.844c42.777 0 93.363.413 113.774 29.737 8.392 12.057 10.446 27.034 6.148 44.632 16.312 17.053 25.063 48.863 16.382 74.757 17.544 23.432 19.143 56.132 9.308 79.469l.11.11c11.893 11.949 19.523 31.259 19.439 49.197-.156 30.352-26.157 58.098-59.553 58.098H350.723C358.03 364.34 384 388.132 384 430.548 384 504 336 512 312 512z"></path></svg><span class="action-number">${data[i].fields.downNumber} </span>
                                <svg class="post-action repost" aria-hidden="true" data-prefix="fas" data-icon="sync-alt" class="svg-inline--fa fa-sync-alt fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="blue" d="M370.72 133.28C339.458 104.008 298.888 87.962 255.848 88c-77.458.068-144.328 53.178-162.791 126.85-1.344 5.363-6.122 9.15-11.651 9.15H24.103c-7.498 0-13.194-6.807-11.807-14.176C33.933 94.924 134.813 8 256 8c66.448 0 126.791 26.136 171.315 68.685L463.03 40.97C478.149 25.851 504 36.559 504 57.941V192c0 13.255-10.745 24-24 24H345.941c-21.382 0-32.09-25.851-16.971-40.971l41.75-41.749zM32 296h134.059c21.382 0 32.09 25.851 16.971 40.971l-41.75 41.75c31.262 29.273 71.835 45.319 114.876 45.28 77.418-.07 144.315-53.144 162.787-126.849 1.344-5.363 6.122-9.15 11.651-9.15h57.304c7.498 0 13.194 6.807 11.807 14.176C478.067 417.076 377.187 504 256 504c-66.448 0-126.791-26.136-171.315-68.685L48.97 471.03C33.851 486.149 8 475.441 8 454.059V320c0-13.255 10.745-24 24-24z"></path></svg><span class="action-number">${data[i].fields.repostNumber} </span>     
                                <span class="post-date">${data[i].fields.postedOn}</span>
                            </div>
                            </div>
                        </div>`;
                        $(".load-more").before(post);
                        if (data[i].up == 'False'){
                            $(`svg#up-${data[i].pk}`).children(":first").attr("fill", "#333");
                        }
                        if (data[i].down == 'False'){
                            $(`svg#down-${data[i].pk}`).children(":first").attr("fill", "#333");
                        }
                    }
                    TrimContent();
                    handleAction((numberOfLoad-1)*10, (numberOfLoad-1)*10+data.length, token);
                }
                //If there is no more posts to load, show message
                else {
                    if ($("#no-more-posts").length == 0)
                        $(".load-more").before("<p id='no-more-posts'>There are no more posts to show.</p>");
                    $(".load-more").css("display", "none");
                }
            });
        }, 1000);
    }
    });
}

//Handle the actions from user, the first 2 params used identify which posts it will have effect to,
//to prevent the functions from not working after ajax call
function handleAction(startNumber, stopNumber, token) {
    //Up action
    $(".up").each((index, value) => {
        if (index >= startNumber && index <= stopNumber) {
            let up = $(".up").eq(index);
            let postId = up.parent().children(":first").attr('id');
            up.on("click", () => {
                $.ajax({
                    type: "post",
                    data: {
                        up: postId,
                        csrfmiddlewaretoken: token,
                    }
                }).done((data) => {
                    data = JSON.parse(data);
                    //Change the status of the up and down buttons
                    if (data['userUp'] == 'True') {
                        up.children(":first").attr("fill", "green");
                    }
                    else if (data['userUp'] == 'False') {
                        up.children(":first").attr("fill", "#333");
                    }
                    up.next().html(`${data['up']}`);
                    let down = up.next().next();
                    down.children(":first").attr("fill", "#333");
                    down.next().html(`${data['down']}`);
                });
            });
        }
    });

    //Down Action
    $(".down").each((index, value) => {
        if (index >= startNumber && index <= stopNumber) {
            let down = $(".down").eq(index);
            let postId = down.parent().children(":first").attr('id');
            down.on("click", () => {
                $.ajax({
                    type: "post",
                    data: {
                        down: postId,
                        csrfmiddlewaretoken: token,
                    }
                }).done((data) => {
                    data = JSON.parse(data);
                    //Change the status of the up and down buttons
                    if (data['userDown'] == 'True') {
                        down.children(":first").attr("fill", "red");
                    }
                    else if (data['userDown'] == 'False') {
                        down.children(":first").attr("fill", "#333");
                    }
                    down.next().html(`${data['down']}`);
                    let up = down.prev().prev();
                    up.children(":first").attr("fill", "#333");
                    up.next().html(`${data['up']}`);
                })
            })
        }
    });
}

//Centered the load more icon
function adjustLoadingPos() {
    let loadMore = $(".load-more")
    loadMore.css("margin-left", `${($(".middle").width()-loadMore.width())/2}`);
}