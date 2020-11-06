package com.example.wheelchairmonitoringapp.ui.main;

import android.content.Context;

import androidx.annotation.Nullable;
import androidx.annotation.StringRes;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentPagerAdapter;

import com.example.wheelchairmonitoringapp.R;
import com.github.nkzawa.socketio.client.Socket;

public class SectionsPagerAdapter extends FragmentPagerAdapter {

    @StringRes
    private static final int[] TAB_TITLES = new int[]{R.string.ecg_tab, R.string.gsr_tab, R.string.pm_tab, R.string.wm_tab};
    private final Context mContext;
    private Socket socket;


    public SectionsPagerAdapter(Context context, FragmentManager fm, Socket socket) {
        super(fm);
        mContext = context;
        this.socket = socket;
    }

    @Override
    public Fragment getItem(int position) {
        String tab_title = this.mContext.getString(TAB_TITLES[position]).toLowerCase();
        if (position == 0 || position == 1)
            return new Graph_Fragment(tab_title, this.socket);
        return new Matrix_Fragment(tab_title, this.socket, this.mContext);
    }

    @Nullable
    @Override
    public CharSequence getPageTitle(int position) {
        return mContext.getResources().getString(TAB_TITLES[position]);
    }

    @Override
    public int getCount() {
        return TAB_TITLES.length;
    }
}