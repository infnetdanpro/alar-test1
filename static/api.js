function get_user(user_id, callback_success) {
    $.ajax({
        url: `/api/1.0/users/${user_id}`,
        method: 'GET',
        success: callback_success,
        error: response => {
            console.log(response)
        }
    });
}

function create_user(username, password, role_id, callback_success) {
    $.ajax({
        url: '/api/1.0/users',
        method: 'POST',
        data: {username, password, role_id},
        success: callback_success,
        error: response => {
            alert(`Status Code: ${response.status}. Message: ${response.responseJSON.message}.`);

            $(document).ready(function() {
                $('a#delete').on("click", delete_element);
                $('a#edit').on('click', edit_user);
                $('#Modal').modal('hide');
                clear_form();
            });
        }
    });
}

function update_user(user_id, username, password, role_id, callback_success) {
console.log(user_id, username, password, role_id, callback_success)
    let data = {username, role_id};
    if (password !== null) {
        data.password = password
    }
    $.ajax({
        url: `/api/1.0/users/${user_id}`,
        method: 'PUT',
        data: data,
        success: callback_success,
        error: response => {
            alert(`Status Code: ${response.status}. Message: ${response.responseJSON.message}.`);

            $(document).ready(function() {
//                $('a#edit').on("click", delete_element);
                $('#Modal').modal('hide');
                clear_form();
            });
        }
    });
}

function delete_user(user_id, callback_success, callback_error) {
        $.ajax({
            url: `/api/1.0/users/${user_id}`,
            method: "DELETE",
            data: {user_id: user_id},
            success: callback_success,
            error: response => {
                if (response.status === 403) {
                    alert("You don't have access to use this function!");
                }
                else if (response.status === 406) {
                    alert(response.responseJSON.message);
                }
                else if (response.status === 503) {
                    alert('Error on the server: 503');
                }
                else {
                    alert('Error');
                }
            }
        });
    }

function clear_form(){
  $('.username').val('');
  $('.password').val('');
  return true
}

function delete_element(e) {
    e.preventDefault()
    let user_id = $(this).data("user-id");
    if (confirm("Are you sure want to delete this user?")) {
        delete_user(user_id, success => {
            $(`tr.user-${user_id}`).remove();
        })
    }
}

function on_delete(element){
    $(element).on("click", delete_element);
}

function off_delete(element) {
    $(element).off();
    $('button.submit').off();
    console.log("off", element)
}

$(document).ready(function() {
    on_delete('a#delete');
});

$('#Modal').on('show.bs.modal', function (event) {
  let button = $(event.relatedTarget)
  let action = button.data('action')
  let modal = $(this);

  clear_form();
  let $username = $('.username');
  let $password = $('.password');
  let $role = $('.roles');
  if (action === 'newUser') {
    modal.find('.modal-title').text('Create user')
    $('.roles').val(1);
  }
  if (action === 'edit') {
    modal.find('.modal-title').text('Edit user')
  }

  $('button.submit').on('click', function(event) {
    event.preventDefault();
    if (action === 'newUser') {
        create_user($username.val(), $password.val(), $role.val(), response => {
            off_delete('a#delete')
            get_user(response.user_id, success => {
                let $new_row = $('tr').last();
                $new_row.after(`
                <tr class="user-${success.user_id}">
                    <td>${success.user_id}</td>
                    <td>${success.username}</td>
                    <td>${success.role}</td>
                    <td>[<a href="#" id="edit" data-user-id="${success.user_id}">Edit</a>] | [<a href="#" id="delete" data-user-id="${success.user_id}">Delete</a>]</td>
                </tr>`);

                $(document).ready(function() {
                    $('a#delete').on("click", delete_element);
                    $('a#edit').on('click', edit_user);
                    modal.modal('hide');
                });
            });
        });
    }
  });
});
$('#Modal').on('hidden.bs.modal', function () {
    clear_form();
    $('button.submit').off();
})


function edit_user(event){
    event.preventDefault();
    let $edit_element = $(this);
    let user_id = $edit_element.data('userId');

    off_delete()
    get_user(user_id, response => {
        clear_form();
        $("#Modal").modal('show');
        $('.username').val(response.username);
        $('.password').focus(() => {
            $('.password').val("");
        })

        $(`.roles option[value="${response.role_id}"]`).attr('selected','selected');
        $('button.submit').on('click', function(event) {
        let new_password = null;
        update_user(user_id, $('.username').val(), $('.password').val(), $('.roles').val(), success => {
            $(`td.role-${user_id}`).text($('.roles option:selected').text());
            console.log($('.username').val());
            $(`td.username-${user_id}`).text($('.username').val());

            $(document).ready(function() {
                $('a#edit').on('click', edit_user);
                $("#Modal").modal("hide");
            });
        });
    });
    });
}
$('a#edit').on('click', edit_user);