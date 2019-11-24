var users = [
  {
    id: 1,
    name: "Bob",
    address: "Manila",
    age: 27
  },
  {
    id: 2,
    name: "Harry",
    address: "Baguio",
    age: 32
  }
];

$.each(users, function(i, user) {
  appendToUsrTable(user);
});

$("form").submit(function(e) {
  e.preventDefault();
});

$("form#addUser").submit(function() {
  var user = {};
  var nameInput = $('input[name="nombre"]').val().trim();
  var addressInput = $('input[name="contra"]').val().trim();
  var ageInput = $('input[name="tipo"]').val().trim();
  if (nameInput && addressInput && ageInput) {
    $(this).serializeArray().map(function(data) {
      user[data.name] = data.value;
    });
    var lastUser = users[Object.keys(users).sort().pop()];
    user.id = lastUser.id + 1;

    addUser(user);
  } else {
    alert("Todos los campos tienen que tener un valor y que éste sea válido.");
  }
});

function addUser(user) {
  users.push(user);
  appendToUsrTable(user);
}

function editUser(id) {
  users.forEach(function(user, i) {
    if (user.id == id) {
      $(".modal-body").empty().append(`
                <form id="updateUser" action="">
                    <label for="nombre">Nombre</label>
                    <input class="form-control" type="text" name="nombre" value="${user.name}"/>
                    <label for="contra">Contraseña</label>
                    <input class="form-control" type="text" name="contra" value="${user.address}"/>
                    <label for="tipo">Tipo de usuario</label>
                    <input class="form-control" type="text" name="tipo" value="${user.age}" />
            `);
      $(".modal-footer").empty().append(`
                    <button type="button" type="submit" class="btn btn-primary" onClick="updateUser(${id})">Guardar cambios</button>
                    <button type="button" class="btn btn-default" data-dismiss="modal">Cerrar</button>
                </form>
            `);
    }
  });
}

function deleteUser(id) {
  var action = confirm("¿Estás seguro de querer eliminar este usuario?");
  var msg = "Usuario eliminado";
  users.forEach(function(user, i) {
    if (user.id == id && action != false) {
      users.splice(i, 1);
      $("#userTable #user-" + user.id).remove();
      flashMessage(msg);
    }
  });
}

function updateUser(id) {
  var msg = "Usuario Actualizado correctamente";
  var user = {};
  user.id = id;
  users.forEach(function(user, i) {
    if (user.id == id) {
      $("#updateUser").children("input").each(function() {
        var value = $(this).val();
        var attr = $(this).attr("nombre");
        if (attr == "nombre") {
          user.name = value;
        } else if (attr == "contra") {
          user.address = value;
        } else if (attr == "tipo") {
          user.age = value;
        }
      });
      users.splice(i, 1);
      users.splice(user.id - 1, 0, user);
      $("#userTable #user-" + user.id).children(".userData").each(function() {
        var attr = $(this).attr("nombre");
        if (attr == "nombre") {
          $(this).text(user.name);
        } else if (attr == "contra") {
          $(this).text(user.address);
        } else {
          $(this).text(user.age);
        }
      });
      $(".modal").modal("toggle");
      flashMessage(msg);
    }
  });
}

function flashMessage(msg) {
  $(".flashMsg").remove();
  $(".row").prepend(`
        <div class="col-sm-12"><div class="flashMsg alert alert-success alert-dismissible fade in" role="alert"> <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button> <strong>${msg}</strong></div></div>
    `);
}

function appendToUsrTable(user) {
  $("#userTable > tbody:last-child").append(`
        <tr id="user-${user.id}">
            <td class="userData" name="nombre">${user.name}</td>
            '<td class="userData" name="contra">${user.contra}</td>
            '<td id="tdAge" class="userData" name="tipo">${user.tipo}</td>
            '<td align="center">
                <button class="btn btn-success form-control" onClick="editUser(${user.id})" data-toggle="modal" data-target="#myModal")">Editar</button>
            </td>
            <td align="center">
                <button class="btn btn-danger form-control" onClick="deleteUser(${user.id})">Eliminar</button>
            </td>
        </tr>
    `);
}