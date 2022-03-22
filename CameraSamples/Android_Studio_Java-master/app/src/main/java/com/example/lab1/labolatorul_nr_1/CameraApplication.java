package com.example.lab1.labolatorul_nr_1;

import android.app.Activity;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v4.app.NotificationCompat;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.RadioGroup;

import java.util.Timer;
import java.util.TimerTask;

public class CameraApplication extends AppCompatActivity {

    private EditText inputGoogle;
    private ImageView cameraPicture;
    private String googleBaseUrl = "http://www.google.com/search?q=";

    public static final int CAMERA_REQUEST = 1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_camera_application);

        defineButtons();
    }

    public void defineButtons() {
        findViewById(R.id.button).setOnClickListener(buttonClickListener);
        findViewById(R.id.button2).setOnClickListener(buttonClickListener);
        findViewById(R.id.A).setOnClickListener(buttonClickListener);
        findViewById(R.id.B).setOnClickListener(buttonClickListener);

        cameraPicture = (ImageView) findViewById(R.id.cameraPicture);

        Button one = (Button) this.findViewById(R.id.button4);

        final MediaPlayer mp = MediaPlayer.create(this, R.raw.train);

        one.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mp.start();
            }
        });

        inputGoogle = (EditText) findViewById(R.id.editText);
    }

    private View.OnClickListener buttonClickListener = new View.OnClickListener() {

        @Override
        public void onClick(View v) {
            switch (v.getId()) {
                case R.id.button2:
                    new Timer().schedule(new TimerTask() {
                        @Override
                        public void run() {
                            NotificationCompat.Builder mBuilder =
                                    new NotificationCompat.Builder(CameraApplication.this)
                                            .setSmallIcon(R.drawable.notification_icon)
                                            .setContentTitle("Notification after 10 seconds")
                                            .setContentText("Priveeeeeeeeeeeeeet!")
                                            .setAutoCancel(true);

                            NotificationManager mNotificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
                            mNotificationManager.notify(001, mBuilder.build());
                        }
                    }, 10000);

                    break;
                case R.id.button:
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(googleBaseUrl + inputGoogle.getText())));
                    break;
                case R.id.A:
                    Intent launchIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
                    launchIntent.putExtra("android.intent.extras.CAMERA_FACING", android.hardware.Camera.CameraInfo.CAMERA_FACING_FRONT);
                    launchIntent.putExtra("android.intent.extras.LENS_FACING_FRONT", 1);
                    launchIntent.putExtra("android.intent.extra.USE_FRONT_CAMERA", true);
                    startActivityForResult(launchIntent, CAMERA_REQUEST);
                    break;
                case R.id.B:
                    Intent launchIntent2 = new Intent(MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA);
                    launchIntent2.putExtra("android.intent.extras.CAMERA_FACING", android.hardware.Camera.CameraInfo.CAMERA_FACING_BACK);
                    launchIntent2.putExtra("android.intent.extras.LENS_FACING_BACK", 1);
                    launchIntent2.putExtra("android.intent.extra.USE_BACK_CAMERA", true);
                    startActivity(launchIntent2);
                    startActivityForResult(launchIntent2, CAMERA_REQUEST);
                    break;
            }
        }
    };

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == CAMERA_REQUEST && resultCode == Activity.RESULT_OK) {
            Bitmap photo = (Bitmap) data.getExtras().get("data");
            cameraPicture.setImageBitmap(photo);
        }
    }
}