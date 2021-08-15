using UnityEngine;
using System.Collections;

public class CameraMovement : MonoBehaviour {

    private enum CameraMode
    {
        OnePlayer,
        TwoPlayers,
        None
    }

    [SerializeField] float movementSpeed = 10;
    private Transform _player1;
    private Transform _player2;
    private Transform _observedPlayer;

    private Camera _camera;

    private CameraMode _cameraMode;
    private float _cameraStartY;
    private float _cameraZoomSpeed = 8f;

    private bool _stretchedCauseOfX = false;
    private bool _stretchedCauseOfY = false;

    private bool _isOnSwitchProcess = false;

    void Start()
    {
        _camera = GetComponent<Camera>();
        _cameraStartY = transform.position.y;

        _player1 = GameController.instance.player1Instance.transform;
        _observedPlayer = _player1;

        if(GameController.instance.player2Instance != null)
        {
            _player2 = GameController.instance.player2Instance.transform;
        }

        if (_player2 != null)
        {
            _cameraMode = CameraMode.TwoPlayers;
        }
        else
        {
            _cameraMode = CameraMode.OnePlayer;
        }
    }

    void FixedUpdate()
    {
        Vector3 cameraDelta = Vector3.zero;

        Ray newRay = new Ray(transform.position, transform.forward);
        RaycastHit hitInfo;

        if (Physics.Raycast(newRay, out hitInfo, Mathf.Infinity, 1 << LayerMask.NameToLayer("Ground")))
        {
            if (_cameraMode == CameraMode.OnePlayer)
            {
                cameraDelta = _observedPlayer.position - hitInfo.point;
                cameraDelta.y = 0;
            }
            else if (_cameraMode == CameraMode.TwoPlayers)
            {
                cameraDelta = (_player1.position + _player2.position + Vector3.back * (Mathf.Abs(_player1.position.z - _player2.position.z) * .1f ) ) / 2 - hitInfo.point;
                cameraDelta.y = 0;

                Vector3 player1ScreenPos = _camera.WorldToScreenPoint(_player1.position);
                Vector3 player2ScreenPos = _camera.WorldToScreenPoint(_player2.position);

                if(player1ScreenPos.x > Screen.width * (1 - .08)  || player1ScreenPos.x < 0 + Screen.width * .08 ||
                   player2ScreenPos.x > Screen.width * (1 - .08)  || player2ScreenPos.x < 0 + Screen.width * .08)
                {
                    cameraDelta.y = 1;
                    _stretchedCauseOfX = true;
                    _stretchedCauseOfY = false;
                }

                if(player1ScreenPos.y > Screen.height * (1 - .08) || player1ScreenPos.y < 0 + Screen.height * .08 ||
                    player2ScreenPos.y > Screen.height * (1 - .08) || player2ScreenPos.y < 0 + Screen.height * .08)
                {
                    _stretchedCauseOfY = true;
                    _stretchedCauseOfX = false;
                    cameraDelta.y = 1;
                }
                
                if(transform.position.y > _cameraStartY)
                {
                    if (_stretchedCauseOfX &&
                        player1ScreenPos.x < Screen.width * (1 - .12f) && player1ScreenPos.x > 0 + Screen.width * .12f &&
                        player2ScreenPos.x < Screen.width * (1 - .12f) && player2ScreenPos.x > 0 + Screen.width * .12f)
                    {
                        cameraDelta.y = -1;
                    }
                    else if (_stretchedCauseOfY &&
                        player1ScreenPos.y < Screen.height * (1 - .12f) && player1ScreenPos.y > 0 + Screen.height * .12f &&
                        player2ScreenPos.y < Screen.height * (1 - .12f) && player2ScreenPos.y > 0 + Screen.height * .12f)
                    {
                        cameraDelta.y = -1;
                    }
                }
                else
                {
                    _stretchedCauseOfX = false;
                    _stretchedCauseOfY = false;
                }

                if (!_isOnSwitchProcess)
                {
                    if (_player1.GetComponent<LivingEntity>().isDead())
                    {
                        _isOnSwitchProcess = true;
                        StartCoroutine(SwitchFromTwoToOne(_player2));
                    }
                    else if (_player2.GetComponent<LivingEntity>().isDead())
                    {
                        _isOnSwitchProcess = true;
                        StartCoroutine(SwitchFromTwoToOne(_player1));
                    }
                }
            }
        }

        transform.Translate(new Vector3(cameraDelta.x * movementSpeed,
            cameraDelta.y * _cameraZoomSpeed,
            cameraDelta.z * movementSpeed) * Time.fixedDeltaTime, Space.World);
    }

    private IEnumerator SwitchFromTwoToOne(Transform player)
    {
        yield return new WaitForSeconds(5f);

        _observedPlayer = player;
        _cameraMode = CameraMode.OnePlayer;

        float originalMovementSpeed = movementSpeed;
        float currentCameraZoom = transform.position.y;
        float counter = 0;

        while(counter < 3)
        {
            counter += Time.deltaTime;
            movementSpeed = Mathf.Lerp(0, originalMovementSpeed, counter / 3);
            transform.position = new Vector3(transform.position.x, Mathf.Lerp(currentCameraZoom, _cameraStartY, counter / 3), transform.position.z);
            yield return null;
        }

        transform.position = new Vector3(transform.position.x, _cameraStartY, transform.position.z);
        movementSpeed = originalMovementSpeed;
    }
}
