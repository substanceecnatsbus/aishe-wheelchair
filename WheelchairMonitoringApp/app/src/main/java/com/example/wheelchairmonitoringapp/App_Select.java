package com.example.wheelchairmonitoringapp;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;

public class App_Select extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_select);

        // set button text
        Button select_inference_button = (Button) findViewById(R.id.select_inference_button);
        Button select_data_gathering_button = (Button) findViewById(R.id.select_data_gathering_button);
        String[] app_select_strings = getResources().getStringArray(R.array.app_select);
        select_inference_button.setText(app_select_strings[0]);
        select_data_gathering_button.setText(app_select_strings[1]);
    }

    public void on_button_click(View view) {
        // get the text of the button pressed
        Button button = (Button) findViewById(view.getId());
        String button_text = button.getText().toString();

        Intent intent = new Intent(this, App_Main.class);
        intent.putExtra(getString(R.string.selected_app_key), button_text);
        startActivity(intent);
    }

}