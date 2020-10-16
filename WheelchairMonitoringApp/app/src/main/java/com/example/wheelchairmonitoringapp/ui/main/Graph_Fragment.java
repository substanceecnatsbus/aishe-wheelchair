package com.example.wheelchairmonitoringapp.ui.main;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.wheelchairmonitoringapp.R;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;
import com.github.nkzawa.emitter.Emitter;
import com.github.nkzawa.socketio.client.Socket;

import java.util.ArrayList;


public class Graph_Fragment extends Fragment {

    private LineChart line_chart;
    private String name;
    private Socket socket;

    public Graph_Fragment(String name, Socket socket) {
        this.name = name;
        this.socket = socket;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        String event_title_base = "mobile-" + this.name;
        socket.on(event_title_base + "-signal", this.onSignalReceived);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_graph_, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        line_chart = view.findViewById(R.id.chart);
        line_chart.setTouchEnabled(true);
        line_chart.setPinchZoom(true);
        line_chart.getAxisLeft().setDrawGridLines(false);
        line_chart.getXAxis().setDrawGridLines(false);
        line_chart.getXAxis().setPosition(XAxis.XAxisPosition.BOTTOM);
        line_chart.getAxisRight().setDrawGridLines(false);;
        line_chart.getAxisRight().setDrawLabels(false);


        ArrayList<Entry> values = new ArrayList<>();

        LineDataSet dataSet = new LineDataSet(values, this.name.toUpperCase());
        dataSet.setDrawValues(false);
        dataSet.setDrawCircles(false);

        ArrayList<ILineDataSet> dataSets = new ArrayList<>();
        dataSets.add(dataSet);

        final LineData data = new LineData(dataSets);
        line_chart.setData(data);
        line_chart.invalidate();
    }

    private Emitter.Listener onSignalReceived = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            String[] value_pair = args[0].toString().split(",");
            final long t = Long.parseLong(value_pair[0]);
            final float y = Float.parseFloat(value_pair[1]);
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    LineData ld = line_chart.getLineData();

                    if(ld.getEntryCount() > 150) {
                        ld.removeEntry(0, 0);
                        line_chart.notifyDataSetChanged();
                        line_chart.invalidate();
                    }

                    Entry e = new Entry(t, y);
                    ld.addEntry(e, 0);
                    line_chart.notifyDataSetChanged();
                    line_chart.invalidate();

                }
            });
        }
    };
}