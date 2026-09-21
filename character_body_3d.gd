extends CharacterBody3D

const WALK_SPEED = 5.0
const RUN_SPEED = 8.5
const JUMP_VELOCITY = 4.5
const MOUSE_SENSITIVITY = 0.003

# Узел камеры или точка обзора (если камера лежит внутри этого узла)
@onready var camera_pivot: Node3D = $CameraPivot if has_node("CameraPivot") else self

func _ready() -> void:
 # Захватываем курсор мыши в центр экрана
 Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
 # Вращение мышей
 if event is InputEventMouseMotion:
  # Поворот персонажа по горизонтали (влево/вправо)
  rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
  
  # Поворот камеры по вертикали (вверх/вниз)
  if camera_pivot != self:
   camera_pivot.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
   camera_pivot.rotation.x = clamp(camera_pivot.rotation.x, deg_to_rad(-89), deg_to_rad(89))

# Нажатие Esc, чтобы освободить мышку и выйти в главное меню
 if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
  Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
  get_tree().change_scene_to_file("res://control.tscn")

func _physics_process(delta: float) -> void:
 # Гравитация
 if not is_on_floor():
  velocity += get_gravity() * delta

 # Прыжок по Пробелу
 if Input.is_action_just_pressed("ui_accept") and is_on_floor():
  velocity.y = JUMP_VELOCITY

 # Бег при зажатом Shift
 var current_speed = WALK_SPEED
 if Input.is_key_pressed(KEY_SHIFT):
  current_speed = RUN_SPEED

 # Прямое считывание клавиш WASD
 var input_dir := Vector2.ZERO
 if Input.is_key_pressed(KEY_W):
  input_dir.y -= 1
 if Input.is_key_pressed(KEY_S):
  input_dir.y += 1
 if Input.is_key_pressed(KEY_A):
  input_dir.x -= 1
 if Input.is_key_pressed(KEY_D):
  input_dir.x += 1
  
 input_dir = input_dir.normalized()
 
 # Переводим направление под взгляд персонажа
 var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
 
 if direction:
  velocity.x = direction.x * current_speed
  velocity.z = direction.z * current_speed
 else:
  velocity.x = move_toward(velocity.x, 0, current_speed)
  velocity.z = move_toward(velocity.z, 0, current_speed)

 move_and_slide()
