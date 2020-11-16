package com.example.wheelchairmonitoringapp;


import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.viewpager.widget.ViewPager;

import com.example.wheelchairmonitoringapp.ui.main.SectionsPagerAdapter;

import com.github.nkzawa.emitter.Emitter;
import com.github.nkzawa.socketio.client.IO;
import com.github.nkzawa.socketio.client.Socket;
import com.google.android.material.tabs.TabLayout;

public class App_Main extends AppCompatActivity {

    private Socket socket;
    private LinearLayout footer;
    private String selected_app;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_app__main);

        // setup socket
        try {
            this.socket = IO.socket(getString(R.string.server_address));
        } catch (Exception e) {
            e.printStackTrace();
        }
        this.socket.connect();

        // set up graphs
        SectionsPagerAdapter sectionsPagerAdapter = new SectionsPagerAdapter(this, getSupportFragmentManager(), socket);
        ViewPager viewPager = findViewById(R.id.graph_view_pager);
        viewPager.setAdapter(sectionsPagerAdapter);
        TabLayout tabs = findViewById(R.id.tabs);
        tabs.setupWithViewPager(viewPager);

        // set up footer
        Intent intent = getIntent();
        Bundle b = intent.getExtras();
        this.selected_app = b.getString(getString(R.string.selected_app_key));
        this.footer = (LinearLayout) findViewById(R.id.footer);
        createFooter();

    }

    private void createFooter() {
        String[] app_select_options = getResources().getStringArray(R.array.app_select);
        if (selected_app.equals(app_select_options[0])) {
            footer_inference();
        } else if (selected_app.equals(app_select_options[1])) {
            footer_data_gathering();;
        }
    }

    private void footer_data_gathering() {
        // create the radio group and add buttons
        final RadioGroup radioGroup = new RadioGroup(this);
        RadioButton discomfort_0 = new RadioButton(this);
        discomfort_0.setText(R.string.discomfort_level_0);
        radioGroup.addView(discomfort_0);

        RadioButton discomfort_1 = new RadioButton(this);
        discomfort_1.setText(R.string.discomfort_level_1);
        radioGroup.addView(discomfort_1);

        RadioButton discomfort_2 = new RadioButton(this);
        discomfort_2.setText(R.string.discomfort_level_2);
        radioGroup.addView(discomfort_2);

        RadioButton discomfort_3 = new RadioButton(this);
        discomfort_3.setText(R.string.discomfort_level_3);
        radioGroup.addView(discomfort_3);
        this.footer.addView(radioGroup);
        radioGroup.check(discomfort_0.getId());

        this.socket.on("request-discomfort-level", new Emitter.Listener() {
            @Override
            public void call(Object... args) {
            int radio_button_id = radioGroup.getCheckedRadioButtonId();
            final RadioButton selected_radio_button = radioGroup.findViewById(radio_button_id);
            socket.emit("discomfort-level", selected_radio_button.getText());
            }
        });
    }

    private void footer_inference() {
        // set up discomfort level inference text view
        final TextView discomfort_level_text_view = new TextView(this);
        discomfort_level_text_view.setText(getString(R.string.discomfort_level_default));
        discomfort_level_text_view.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        this.footer.addView(discomfort_level_text_view);

        // set up last updated text view
        final TextView last_updated_text_view = new TextView(this);
        last_updated_text_view.setText(getString(R.string.last_updated_prefix));
        last_updated_text_view.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        this.footer.addView(last_updated_text_view);

        this.socket.on("receive-inference", new Emitter.Listener() {
            @Override
            public void call(Object... args) {
                // receive and parse data
                String[] data = args[1].toString().split(",");
                final String time = data[0];
                final String inference = data[1];
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        // update fields
                        last_updated_text_view.setText(time);
                        discomfort_level_text_view.setText(inference);
                    }
                });
            }
        });
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        this.socket.off();
        this.socket.disconnect();
    }
}