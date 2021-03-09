package com.example.wheelchairmonitoringapp.ui.main;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import com.example.wheelchairmonitoringapp.R;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;
import com.github.nkzawa.emitter.Emitter;
import com.github.nkzawa.socketio.client.Socket;

import java.util.ArrayList;

public class Matrix_Fragment extends Fragment {

    private Socket socket;
    private Context context;
    private String name;

    public Matrix_Fragment(String name, Socket socket, Context context) {
        this.socket = socket;
        this.context = context;
        this.name = name;
    }

    private void create_table(@NonNull View view) {
        TableLayout table_layout = (TableLayout)view.findViewById(R.id.table_layout);
        for (int row = 0; row < 8; row++) {
            TableRow table_row = new TableRow(this.context);
            for (int column = 0; column < 8; column++) {
                TextView text_view = new TextView(this.context);
                int id = Integer.parseInt("69" + Integer.toString(row) + Integer.toString(column));
                text_view.setId(id);
                text_view.setText("0");
                text_view.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
                text_view.setBackground(this.context.getDrawable(R.drawable.border));
                table_row.addView(text_view);
            }
            table_layout.addView(table_row);
        }
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        String event_title_base = "mobile-" + this.name;
        socket.on(event_title_base + "-signal", this.onSignalReceived);
    }

    private Emitter.Listener onSignalReceived = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            String x = args[0].toString().replace("[", "");
            x = x.replace(" ", "");
            final String buffer = x.replace("]", "");
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    final String[] data = buffer.split(",");
                    final int id = Integer.parseInt("69" + data[1] + data[2]);
                    if (getView() != null) {
                        final TextView cell = (TextView) getView().findViewById(id);
                        cell.setText(data[3]);
                    }
                }
            });
        }
    };

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_matrix, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        create_table(view);
    }
}